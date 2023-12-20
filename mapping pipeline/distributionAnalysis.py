# View distribution
import os
import json
from collections import defaultdict
import matplotlib.pyplot as plt

# Store the quantity for each country and city
country_counts = defaultdict(int)
city_counts = defaultdict(int)
provider_counts = defaultdict(int)

# root floder Path
root_folder = 'final_samples_309_v1'

# Iterate through all subfolders
for subdir, _, files in os.walk(root_folder):
    # Iterate through all files in a subfolder
    for file in files:

        if file.startswith('evaluate') and file.endswith('.json'):
            file_path = os.path.join(subdir, file)

            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                country = data.get('Gt_location', {}).get('country')
                city = data.get('Gt_location', {}).get('city')
                provider = data.get('organization_label', {})

                # Add quantity statistics, including null values
                if country:
                    country_counts[str(country)] += 1

                if not country:
                    print(f'null country:{file_path}')

                if city:
                    city_counts[str(city)] += 1

                if provider:
                    provider_counts[str(provider)] += 1

print("Country Counts:")
all_country = 0
for country, count in country_counts.items():
    all_country += 1
    print(f"{country}: {count}")

print(f'number of different countries:{all_country}')

all_city = 0
print("\nCity Counts:")
for city, count in city_counts.items():
    all_city +=1
    print(f"{city}: {count}")

print(f'number of different countries:{all_city}')

all_provider = 0
print("\nProvider Counts:")
for provider, count in provider_counts.items():
    all_provider +=1
    print(f"{provider}: {count}")

print(f'number of different countries:{all_provider}')


# Visualize the distribution of the number of countries
plt.figure(figsize=(12, 6))
plt.bar(country_counts.keys(), country_counts.values())
plt.xlabel('Countries')
plt.ylabel('Count')
plt.title('Distribution of Countries')
plt.xticks(rotation=90)
plt.yticks(range(0, max(country_counts.values()) + 1, 2))
plt.tight_layout()
plt.show()

# Visualize city number distribution
plt.figure(figsize=(12, 6))
plt.bar(city_counts.keys(), city_counts.values())
plt.xlabel('Cities')
plt.ylabel('Count')
plt.title('Distribution of Cities')
plt.xticks(rotation=90)
plt.yticks(range(0, max(city_counts.values()) + 1, 1))
plt.tight_layout()
plt.show()

# Visualize provider number distribution
plt.figure(figsize=(12, 6))
plt.bar(provider_counts.keys(), provider_counts.values())
plt.xlabel('Providers')
plt.ylabel('Count')
plt.title('Distribution of Providers')
plt.xticks(rotation=90)
plt.yticks(range(0, max(provider_counts.values()) + 1, 5))
plt.tight_layout()
plt.show()

