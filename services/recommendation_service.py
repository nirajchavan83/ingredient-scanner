# services/recommendation_service.py

def generate_recommendation(classified_ingredients: list):
    good = moderate = bad = 0
    harmful = []
    details = []

    for row in classified_ingredients:
        impact = row['health_impact'].lower()
        ing = row['ingredient']
        if impact == "bad":
            details.append(f"{ing} is considered harmful and should be avoided.")
            bad += 1
            harmful.append(ing)
        elif impact == "moderate":
            details.append(f"{ing} is moderately risky and should be limited.")
            moderate += 1
        elif impact == "good":
            details.append(f"{ing} is safe and natural.")
            good += 1

    top_bad = harmful[:3]

    if bad >= 2:
        recommendation = "❌ Unhealthy"
        reasons = [
            f"Contains multiple harmful ingredients like {', '.join(top_bad)}.",
            "Not recommended for children.",
            "May cause long-term health risks.",
            "Avoid frequent consumption."
        ]
    elif moderate >= 2:
        recommendation = "⚠ Consume in Moderation"
        reasons = [
            "Includes processed or moderate-risk ingredients.",
            "Can be consumed 1–2 times a week.",
            "Limit usage in children or sensitive individuals."
        ]
    else:
        recommendation = "✅ Healthy"
        reasons = [
            "Mostly natural and healthy ingredients.",
            "Safe for regular consumption.",
            "Low-risk profile."
        ]

    return recommendation, reasons, top_bad


def assess_suitability(classified_ingredients: list):
    unsafe_keywords = ["emulsifier", "preservative", "flavour", "dextrose", "msg", "colour", "additive"]
    all_text = " ".join([row['ingredient'].lower() for row in classified_ingredients])

    return {
        "children": not any(word in all_text for word in unsafe_keywords),
        "pregnant": not any(w in all_text for w in ["msg", "sodium nitrite", "nitrate", "additive"]),
        "daily_use": not any(row['health_impact'].lower() == "bad" for row in classified_ingredients)
    }


def get_health_score(classified_ingredients: list):
    score = 10
    for row in classified_ingredients:
        impact = row['health_impact'].lower()
        if impact == "bad":
            score -= 3
        elif impact == "moderate":
            score -= 1
    return max(score, 0)
