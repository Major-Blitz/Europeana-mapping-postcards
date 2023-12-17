import requests
import json

# Define the API URL and your API key
api_url = "https://api.europeana.eu/record/v2/search.json"
wskey = "your api key"

# Build the parameters for the API request
params = {
    "query": "postcards",
    "wskey": wskey,
    "reusability": "open",
    "media": True,
    "rows": 100,
    "thumbnail": True,
    "cursor": '*',
}

rawData = []
i = 0

while True:
    # Send a GET request
    response = requests.get(api_url, params=params)
    if "nextCursor" not in response.json():
        break
    params['cursor'] = response.json()['nextCursor']
    # Check the response status code
    if response.status_code == 200:
        i += 1
        print("API Response", i)
        temp = response.json()['items']
        rawData.extend(temp) 
    else:
        print(f"API Request Failed with Status Code: {response.status_code}")

# Extract 'id' and 'type' from the raw data
idType = [{'id': obj['id'], 'type': obj['type']} for obj in rawData]

# Filter the values to only include those with type 'IMAGE'
filtered_values = [obj['id'] for obj in idType if obj['type'] == 'IMAGE']
# print(filtered_values)
totalIDs = len(filtered_values)

# Write the filtered data to another JSON file
with open("records.json", "w") as json_file:
    json.dump(filtered_values, json_file, indent=4)

print('Finished, total records:', totalIDs)
