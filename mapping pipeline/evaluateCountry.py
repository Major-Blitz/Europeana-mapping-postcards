import json
import os

def calculate_country_accuracy(gt_location, other_location):
    gt_country = gt_location.get('country')
    other_country = other_location.get('country')

    if gt_country is None:
        if other_country is None:
            return 1
        else:
            return 0
    else:
        if gt_country == other_country:
            return 1
        else:
            return 0

def evaluate_country_accuracy(folder_path, model_location):
    total_files = 0
    total_accuracy = 0
    incorrect_files = []

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.startswith("evaluate") and filename.endswith(".json"):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    gt_location = data['Gt_location']
                    other_location = data[model_location]

                    accuracy = calculate_country_accuracy(gt_location, other_location)

                    if accuracy is not None:
                        total_accuracy += accuracy
                        total_files += 1

                        if model_location == 'GPT4_Gt_location' and accuracy == 0:
                            incorrect_files.append(file_path)

    avg_accuracy = total_accuracy / total_files if total_files > 0 else 0
    return avg_accuracy, incorrect_files

# root folder path
folder_path = 'Ground_Truth_GPT4_withCoordinate_293'

# Calculate the country matching accuracy rate for the three pipelines respectively.
model1_accuracy = evaluate_country_accuracy(folder_path, 'GPT_location')
model2_accuracy = evaluate_country_accuracy(folder_path, 'GPT3_Gt_location')
model3_accuracy, incorrect_files = evaluate_country_accuracy(folder_path, 'GPT4_Gt_location')

print(f"Model 1 Matching Accuracy: {model1_accuracy}")
print(f"Model 2 Matching Accuracy: {model2_accuracy}")
print(f"Model 3 Matching Accuracy: {model3_accuracy}")

if incorrect_files:
    print("\nFile with incorrect country match:")
    for file in incorrect_files:
        print(file)

