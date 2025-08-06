import os
import pickle

BASE_PATH = "model"

def load_pickle(filename):
    with open(os.path.join(BASE_PATH, filename), 'rb') as f:
        return pickle.load(f)

vectorizer = load_pickle("vectorizer.pkl")
cat_model = load_pickle("category_model.pkl")
subcat_model = load_pickle("sub_category_model.pkl")
proc_model = load_pickle("is_processed_model.pkl")
health_model = load_pickle("health_impact_model.pkl")

le_category = load_pickle("le_category.pkl")
le_sub_category = load_pickle("le_sub_category.pkl")
le_processed = load_pickle("le_processed.pkl")
le_health = load_pickle("le_health.pkl")

def classify_ingredients(ingredient_list):
    results = []
    for ingredient in ingredient_list:
        try:
            vector = vectorizer.transform([ingredient])

            cat_pred = cat_model.predict(vector)[0]
            sub_pred = subcat_model.predict(vector)[0]
            proc_pred = proc_model.predict(vector)[0]
            health_pred = health_model.predict(vector)[0]

            result = {
                "ingredient": ingredient,
                "category": le_category.inverse_transform([cat_pred])[0],
                "sub_category": le_sub_category.inverse_transform([sub_pred])[0],
                "is_processed": le_processed.inverse_transform([proc_pred])[0],
                "health_impact": le_health.inverse_transform([health_pred])[0],
            }
            results.append(result)

        except Exception as e:
            results.append({
                "ingredient": ingredient,
                "error": str(e)
            })

    return results
