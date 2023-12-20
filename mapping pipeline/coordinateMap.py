import os
import json
import requests

def get_coordinates(country, city, file_path):
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "country": country,
        "city": city,
        "format": "json",
        "polygon": 1,
        "addressdetails": 1,
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:
            # Get the coordinates of the first address
            latitude = data[0]['lat']
            longitude = data[0]['lon']
            return latitude, longitude
        else:
            return None
    else:
        print(f"Failed to fetch data:{file_path}")
        return None

# Delete existing coordinates
def process_json_files(root_folder):
    for subdir, _, files in os.walk(root_folder):
        for file in files:
            if file.startswith('evaluate') and file.endswith('.json'):
                file_path = os.path.join(subdir, file)
                with open(file_path, 'r', encoding='utf-8') as json_file:
                    data = json.load(json_file)

                    # Check if 'GPT4_Gt_coordinates' field already exists
                    if 'GPT4_Gt_coordinates' in data:
                        del data['GPT4_Gt_coordinates']

                    country = data.get("GPT4_Gt_location", {}).get('country')
                    city = data.get("GPT4_Gt_location", {}).get('city')

                    # Handling cases where country or city is null
                    if country is None:
                        country = ''
                    if city is None:
                        city = ''

                    coordinates = get_coordinates(country, city, file_path)
                    if coordinates:
                        # Update the original JSON data by adding the 'gptCoordinate' field
                        data['GPT4_Gt_coordinates'] = {'latitude': coordinates[0], 'longitude': coordinates[1]}
                        with open(file_path, 'w', encoding='utf-8') as updated_json_file:
                            json.dump(data, updated_json_file, indent=4)
                    else:
                        print(f"Failed to obtain coordinates for {file_path} :{country} - {city}")


# Root folder path
root_directory = 'Ground_Truth_GPT4_withCoordinate_293'

# Process JSON files
process_json_files(root_directory)

