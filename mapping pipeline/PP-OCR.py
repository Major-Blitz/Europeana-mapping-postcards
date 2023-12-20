import os
import json
from paddleocr import PaddleOCR
from langdetect import detect, LangDetectException
import cv2
import numpy as np

def delete_result_files(folder_path):
    # Iterate through each subfolder and delete files with the "result_" prefix and the 'result.json' file
    for subdir in os.listdir(folder_path):
        subdir_path = os.path.join(folder_path, subdir)

        if os.path.isdir(subdir_path):
            for file in os.listdir(subdir_path):
                if file == 'result.json':
                    os.remove(os.path.join(subdir_path, file))


def process_single_image(image_path, ocr_engines):
    image = cv2.imread(image_path)
    engine_results = []

    for engine in ocr_engines:
        ocr_result = engine.ocr(image, cls=True)
        texts_with_confidence = [(result[1][0], result[1][1], tuple(map(tuple, result[0]))) for result in ocr_result]
        average_confidence = np.mean([conf for _, conf, _ in texts_with_confidence])
        engine_results.append((average_confidence, texts_with_confidence))

    # Select the engine with the highest average confidence
    _, best_texts_with_confidence = max(engine_results, key=lambda item: item[0])

    # Convert to the final results format
    final_results = {box: (text, confidence) for text, confidence, box in best_texts_with_confidence}

    return final_results



def process_images(folder_path):
    ocr_engines = [
        PaddleOCR(use_angle_cls=True, lang="latin"),
        PaddleOCR(use_angle_cls=True, lang="arabic"),
        PaddleOCR(use_angle_cls=True, lang="cyrillic")
    ]

    # Iterate through each subfolder
    for subdir in os.listdir(folder_path):
        subdir_path = os.path.join(folder_path, subdir)

        if os.path.isdir(subdir_path):
            # Only process images without the "result_" prefix
            image_files = [file for file in os.listdir(subdir_path) if (file.endswith('.jpg') or file.endswith('.png')) and not file.startswith('result_')]
    

            for image_file in image_files:
                image_path = os.path.join(subdir_path, image_file)
                ocr_result = process_single_image(image_path, ocr_engines)

                # Extract text, coordinates, and confidences
                texts = [text for _, (text, _) in ocr_result.items()]
                coordinates = [box for box in ocr_result.keys()]
                confidences = [confidence for _, (_, confidence) in ocr_result.items()]

                # Detect language
                detected_languages = []
                for text in texts:
                    try:
                        language = detect(text) if text.strip() else 'unknown'
                    except LangDetectException:
                        language = 'undetected'
                    detected_languages.append(language)

                # Save the results
                result = {
                    "texts": texts,
                    "coordinates": coordinates,
                    "confidences": confidences,
                    "languages": detected_languages
                }

                with open(os.path.join(subdir_path, 'result_' + image_file.replace('.jpg', '.json').replace('.png', '.json')), 'w') as f:
                    json.dump(result, f, indent=4)

                # Generate and save images with text boxes

                image = cv2.imread(image_path)
                for box_as_tuple in ocr_result.keys():
                    box = np.array(list(map(list, box_as_tuple)), dtype=np.int32).reshape((-1, 1, 2))
                    cv2.polylines(image, [box], isClosed=True, color=(255, 0, 0), thickness=2)

                result_image_path = os.path.join(subdir_path, 'result_' + image_file)
                cv2.imwrite(result_image_path, image)

# Call the function

folder_path = 'test'

delete_result_files(folder_path) 
