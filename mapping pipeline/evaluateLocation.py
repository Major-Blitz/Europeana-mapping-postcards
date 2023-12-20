import json
import os

def calculate_accuracy(gt_location, other_location):
    gt_country = gt_location.get('country')
    gt_city = gt_location.get('city')

    other_country = other_location.get('country')
    other_city = other_location.get('city')

    if gt_country is None and gt_city is None:
        if other_country is None and other_city is None:
            return 1
        else:
            return 0 
    elif gt_country is None and gt_city is not None:
        if gt_city == other_city:
            return 1
        else:
            return 0
    elif gt_country is not None and gt_city is None:
        if gt_country == other_country:
            return 1
        else:
            return 0
    else:
        if gt_country == other_country and gt_city == other_city:
            return 1
        else:
            return 0

def evaluate_pipeline(folder_path, model_location):
    total_files = 0
    total_accuracy = 0

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.startswith("evaluate") and filename.endswith(".json"):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    gt_location = data['Gt_location']
                    other_location = data[model_location]

                    accuracy = calculate_accuracy(gt_location, other_location)

                    if accuracy is not None:
                        total_accuracy += accuracy
                        total_files += 1

    avg_accuracy = total_accuracy / total_files if total_files > 0 else 0
    return avg_accuracy

# root folder path
folder_path = '/Users/llooyee/Desktop/Ground_Truth_GPT4_withCoordinate_293'

model1_accuracy = evaluate_pipeline(folder_path, 'GPT_location')
model2_accuracy = evaluate_pipeline(folder_path, 'GPT3_Gt_location')
model3_accuracy = evaluate_pipeline(folder_path, 'GPT4_Gt_location')

print(f"Model 1 Location Matching Accuracy: {model1_accuracy}")
print(f"Model 2 Location Matching Accuracy: {model2_accuracy}")
print(f"Model 3 Location Matching Accuracy: {model3_accuracy}")

