# ocr_service.py
import easyocr
import re

def get_reader():
    return easyocr.Reader(['en'], gpu=False)

def extract_ingredients_from_image(image_path):
    try:
        reader = get_reader()  # Lazy loading
        result = reader.readtext(image_path, detail=0)
        full_text = " ".join(result)

        match = re.search(r"(INGREDIENTS|Ingredients|ingredients)[:\-]?\s*(.*)", full_text)
        ingredients_text = match.group(2) if match else full_text

        stop_keywords = ['CONTAINS', 'Contains', 'NUTRITION', 'Nutrition', 'Manufactured']
        for word in stop_keywords:
            if word in ingredients_text:
                ingredients_text = ingredients_text.split(word)[0]

        ingredients_text = re.sub(r"[\(\)\[\]\{\}]", "", ingredients_text)
        ingredients_text = re.sub(r"\d+(\.\d+)?%", "", ingredients_text)
        ingredients_text = re.sub(r"[0-9]{1,3}(\.[0-9]+)?", "", ingredients_text)

        raw_ingredients = re.split(r",|;", ingredients_text)
        clean_ingredients = [i.strip().lower() for i in raw_ingredients if len(i.strip()) > 1]

        return clean_ingredients

    except Exception as e:
        return []
