from openai import OpenAI
import os
import json
import time
import base64
import requests

nullCounter = 0

api_key = "your api key"

client = OpenAI()
folder_path = './samples'


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def is_json_object_empty(json_obj):
    return not bool(json_obj)


def extract_json(raw_string):
    # Find JSON object in the raw string
    json_start = raw_string.find("{")
    json_end = raw_string.find("}", json_start) + 1

    # Extract JSON string
    json_str = raw_string[json_start:json_end]

    # Parse JSON string
    try:
        json_data = json.loads(json_str)
        print('Extracted results:')
        print(json_data)
        return json_data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return


for subdir in os.listdir(folder_path):
    subdir_path = os.path.join(folder_path, subdir)
    if os.path.isdir(subdir_path):
        print(subdir_path)
        for file in os.listdir(subdir_path):
            if file.startswith("evaluate") and file.endswith(".json"):
                print(file)
                with open(os.path.join(subdir_path, file), 'r') as f:
                    data = json.load(f)
                texts_list = data['Gt_text']
                text = ' '.join(texts_list)
                if 'GPT4_Gt_location' in data:
                    country_predicted = data['GPT4_Gt_location']['country']
                    if country_predicted:
                        if not text:
                            print('This image does not have text on it')
                            continue
                        else:
                            print(text)
                            print('The predicted country is', country_predicted)
                            continue
                # Dealing with image
                for image in os.listdir(subdir_path):
                    if image.startswith("image") and image.endswith(".jpg"):
                        break
                print('The image is:', image)
                base64_image = encode_image(os.path.join(subdir_path, image))
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                payload = {
                    "model": "gpt-4-vision-preview",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an assistant with extensive knowledge in geography, history, "
                                       "and culture, particularly excelling in the related fields of Europe."
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Can you extract the text from this postcard image and, based on the "
                                            "texts and the image itself, boldly speculate on its place of origin("
                                            "country and city)?"
                                            "Please return an object with two attributes named 'country' and 'city' in "
                                            "JSON format. If you can only determine the country, that's fine; just assign "
                                            "null to the 'city' attribute. If you have no clue, then return an empty JSON."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 300
                }
                response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                print(response.json())


                GPTresult = response.json()["choices"][0]["message"]["content"]
                print('GPTresult:', GPTresult)

                location = extract_json(GPTresult)
                if is_json_object_empty(location):
                    print("location JSON object is empty.")
                    nullCounter += 1
                    location = {}
                    # Add new attributes A and B and set them to null
                    location['city'] = None
                    location['country'] = None
                data['GPT4_Gt_location'] = location
                with open(os.path.join(subdir_path, file), 'w', encoding='utf-8') as f1:
                    json.dump(data, f1, ensure_ascii=False, indent=2)
                time.sleep(1)
        os.chdir(folder_path)
print('Finished')
print('nullCounter:', nullCounter)
