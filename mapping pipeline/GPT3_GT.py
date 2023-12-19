from openai import OpenAI
import os
import json
import time

textCounter = 0
notextCounter = 0
nullCounter = 0

os.environ['OPENAI_API_KEY'] = "your api key"

client = OpenAI()
folder_path = './samples'


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
                if 'GPT3_Gt_location' in data:
                    country_predicted = data['GPT3_Gt_location']['country']
                    if country_predicted:
                        if not text:
                            print('This image does not have text on it')
                            notextCounter += 1
                        else:
                            print(text)
                            print('The predicted country is', country_predicted)
                        continue
                    else:
                        nullCounter += 1
                        print(text)
                # GPT processing
                textCounter += 1
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system",
                        "content": "You are an assistant with extensive knowledge in geography, history, and culture, particularly excelling in the related fields of Europe."},
                        {"role": "user",
                        "content": "I used OCR to extract text from a postcard, but there may be spelling errors. Can you venture to help me guess where the postcard came from (country and city in English) based on this text? The text is as follows:" + text +
                                    ". Please just return an object with two attributes named 'country' and 'city' in JSON format. If you can only determine the country, that's fine; just assign null to the 'city' attribute. If you have no clue, then return an empty JSON."
                        }
                    ]
                )
                GPTresult = completion.choices[0].message.content
                print('GPTresult:', GPTresult)

                location = extract_json(GPTresult)
                if is_json_object_empty(location):
                    print("location JSON object is empty.")
                    location = {}
                    # Add new attributes A and B and set them to null
                    location['city'] = None
                    location['country'] = None
                data['GPT3_Gt_location'] = location
                with open(os.path.join(subdir_path, file), 'w', encoding='utf-8') as f1:
                    json.dump(data, f1, ensure_ascii=False, indent=2)
                time.sleep(5)  # Sleep for 20 seconds
        os.chdir(folder_path)
print('Finished')
print('textCounter:', textCounter)
print('notextCounter:', notextCounter)
print('nullCounter:', nullCounter)
