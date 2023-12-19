import json
import shutil
import pyeuropeana.apis as apis
import os
import pandas as pd
import requests
from collections import defaultdict

os.environ['EUROPEANA_API_KEY'] = "your api key"

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
os.makedirs('oneImageWithMetadata', exist_ok=True)

new_dir = 'oneImageWithMetadata'

df = pd.read_csv('records.csv')
# Randomly select 30000 data from the list
sampled_data = df.sample(n=30000)
# Initialize a counter
counter = 0
sample_counter = 0

# Create a dictionary to track how many objects have been selected for each A attribute value
provider_counts = defaultdict(int)

for index, row in sampled_data.iterrows():
    record_link = row['ID']
    if record_link == 'ID':
        continue
    sample_counter += 1
    print("Sampling number", sample_counter, ":")
    try:
        data = apis.record(record_link)
    except Exception as e:
        print(e)
        continue
    # Filter data using the filter_data function
    filtered_data = filter_data(data)
    # If the same provider appears more than 5 times
    if provider_counts[filtered_data['organization_label'][0]] >= 30:
        print('The provider limit reached for:', filtered_data['organization_label'][0])
        continue
    # Build the file name, for example, get the ID from the record link and use it as the file name
    record_id = record_link.split('/')[-1]

    filtered_file_name = f'{record_id}.json'
    # Change to the new directory
    os.chdir(new_dir)
    # Create the folder
    folder_name = f'{record_id}'
    os.makedirs(folder_name, exist_ok=True)

    os.chdir(folder_name)
    # Image counter
    SN = 0
    if isinstance(filtered_data, dict) and 'webResources' in filtered_data:
        A_value = filtered_data['webResources']
        # If A_value is a list
        if isinstance(A_value, list):
            # Iterate over each object in the A_value list
            for obj in A_value:
                # Ensure the object has the B property
                if isinstance(obj, dict) and 'about' in obj:
                    # Assume this is your URL link
                    url = obj['about']
                    try:
                        # Send HTTP request and get response
                        response = requests.head(url, timeout=10)  # Use HEAD request to only get response headers
                        if response.headers.get('content-type', '').startswith('image'):
                            SN += 1
                            if SN > 1:
                                break
                            responseImage = requests.get(url)
                            with open('image' + '_' + str(SN) + '_' + record_id + '.jpg', 'wb') as f:
                                f.write(responseImage.content)
                    except requests.Timeout:
                        print("Request timed out")
                    except requests.ConnectionError:
                        # Catch connection issues
                        print("Connection error occurred")
                    except requests.RequestException as e:
                        # Catch other request exceptions
                        print(f"Request failed: {e}")
    if SN > 1:
        print('ID:', record_link, ', has multiple images')
        # Ensure the folder path you want to delete is correct to avoid accidentally deleting other content
        if folder_name.endswith('/'):
            print("Please make sure the folder path doesn't end with a '/' character.")
        else:
            try:
                # Delete a non-empty folder
                os.chdir('..')
                shutil.rmtree(folder_name)
                print(f'The folder {folder_name} has been deleted')
            except Exception as e:
                print(f'Error: {e}')
    elif SN == 1:
        print(f"Folder {folder_name} has only one image, writing metadata")

        with open(filtered_file_name, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, indent=4)
        counter += 1
        provider_counts[filtered_data['organization_label'][0]] += 1
        print(counter, ":", record_link, 'has been written')
        if counter >= 650:
            break
    else:
        try:
            # Delete an empty folder
            os.chdir('..')
            os.rmdir(folder_name)
            print(f"Empty folder {folder_name} has been deleted")
        except OSError as e:
            print(f'Error: {e}')
print('Finished, you have', counter, 'images')
