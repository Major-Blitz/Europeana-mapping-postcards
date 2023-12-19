import json
import pyeuropeana.apis as apis
import os
import pandas as pd
import requests

os.environ['EUROPEANA_API_KEY'] = "heviandec"

def filter_data(data):
    filtered_data = {
        "aggregations_about": get_value(data, ["object", "aggregations", 0, "about"], "not showed"),
        "webResources": get_value(data, ["object", "aggregations", 0, "webResources"], "not showed"),
        "concept_label": get_value(data, ["object", "concepts", 0, "prefLabel", "en"], "not showed"),
        "concept_note": get_value(data, ["object", "concepts", 0, "note", "en"], "not showed"),
        "edmDatasetName": get_value(data, ["object", "edmDatasetName"], "not showed"),
        "edmCountry": get_value(data, ["object", "europeanaAggregation", "edmCountry", "def"], "not showed"),
        "edmLanguage": get_value(data, ["object", "europeanaAggregation", "edmLanguage", "def"], "not showed"),
        "organization_label": get_value(data, ["object", "organizations", 0, "prefLabel", "en"], "not showed"),
        "coordinate": get_place(data, "not showed")
    }
    return filtered_data

def get_value(data, keys, default):
    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        elif isinstance(data, list) and isinstance(key, int) and key < len(data):
            data = data[key]
        else:
            return default
    return data

def get_place(data, default):
    latitude_longitude_pairs = []

    def recursive_search(data):
        if isinstance(data, dict):
            if 'latitude' in data and 'longitude' in data:
                latitude_longitude_pairs.append((data['latitude'], data['longitude']))
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    recursive_search(value)
        elif isinstance(data, list):
            for item in data:
                recursive_search(item)

    recursive_search(data)
    if not latitude_longitude_pairs:
        return default

    return latitude_longitude_pairs

# Ensure the target folder exists
os.makedirs('metaDataWithImages', exist_ok=True)

new_dir = '/Users/liujingbang/PycharmProjects/locationDeduction/metaDataWithImages'

df = pd.read_csv('records.csv')


sampled_data = df
# Adjust data segment size here
# sampled_data = df.iloc[:19793]


# Valid id counter
idCounter = 0
# Image count counter
imageCounter = 0
# Invalid id counter
badCounter = 0
# DataFrame id counter
dfId = 0

for index, row in sampled_data.iterrows():
    record_link = row['ID']
    dfId += 1
    if record_link == 'ID':
        continue
    flag = 0
    # Fetch record data from europeana
    data = apis.record(record_link)
    # Filter data using filter_data function
    filtered_data = filter_data(data)
    # Build filename, for example, get the ID from the record link and use it as the filename
    record_id = record_link.split('/')[-1]
    filtered_file_name = f'{record_id}.json'

    os.chdir(new_dir)
    counter = 0
    if isinstance(filtered_data, dict) and 'webResources' in filtered_data:
        A_value = filtered_data['webResources']

        if isinstance(A_value, list):
            for obj in A_value:

                if isinstance(obj, dict) and 'about' in obj:

                    url = obj['about']
                    try:
                        # Send HTTP request and get response
                        response = requests.head(url, timeout=10)
                        if response.headers.get('content-type', '').startswith('image'):
                            responseImage = requests.get(url)
                            if responseImage.status_code == 200 and responseImage.content:
                                counter += 1
                                imageCounter += 1
                                flag = 1
                    except requests.Timeout:
                        print("Request timed out")
                    except requests.ConnectionError:
                        # Catch connection issues
                        print("Connection error occurred")
                    except requests.RequestException as e:
                        # Catch other request exceptions
                        print(f"Request failed: {e}")

                        # If it's a single object
        elif isinstance(A_value, dict) and 'about' in A_value:
            # Assume this is your URL link
            url = A_value['about']
            try:
                # Send HTTP request and get response
                response = requests.head(url, timeout=10)
                if response.headers.get('content-type', '').startswith('image'):
                    responseImage = requests.get(url)
                    if responseImage.status_code == 200 and responseImage.content:
                        counter += 1
                        imageCounter += 1
                        flag = 1
            except requests.Timeout:
                print("Request timed out")
            except requests.ConnectionError:
                # Catch connection issues
                print("Connection error occurred")
            except requests.RequestException as e:
                # Catch other request exceptions
                print(f"Request failed: {e}")

        # Save metadata with accessible images
        if flag == 1:
            with open(filtered_file_name, 'w', encoding='utf-8') as f:
                json.dump(filtered_data, f, indent=4)
                idCounter += 1
            print('DF index', index, '-', idCounter, ":", record_link, 'is valid, which has', counter, 'images')
        else:
            print(record_link, 'cannot access to the images.')
            badCounter += 1
print('Finished')
print('Total valid id: ', idCounter)
print('Total images: ', imageCounter)
print('Total useless id: ', badCounter)
print('DF id: ', dfId)
