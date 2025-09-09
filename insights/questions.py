# insights/questions.py

# Questions + options with scores
QUESTIONNAIRE = [
    {
        "code": "A1",
        "text": "Typical weekday outdoor time between 10am–3pm:",
        "options": [
            {"label": "≥ 30 min", "score": 0},
            {"label": "10–29 min", "score": 8},
            {"label": "< 10 min", "score": 14},
        ],
    },
    {
        "code": "A2",
        "text": "Work/study pattern:",
        "options": [
            {"label": "Mostly outdoor", "score": 0},
            {"label": "Mixed", "score": 2},
            {"label": "Mostly indoor / night-shift", "score": 6},
        ],
    },
    {
        "code": "B",
        "text": "Skin type — Fitzpatrick:",
        "options": [
            {"label": "I–II (very fair / fair)", "score": 0},
            {"label": "III–IV (medium / olive)", "score": 8},
            {"label": "V–VI (dark / very dark)", "score": 15},
        ],
    },
    {
        "code": "C",
        "text": "Location & season for the next 2–3 months:",
        "helper": "Choose the highest that applies.",
        "options": [
            {"label": "QLD/NT year-round OR WA/NSW summer/spring", "score": 0},
            {"label": "NSW/WA autumn/winter OR SA spring", "score": 6},
            {"label": "VIC/TAS/ACT in autumn/winter", "score": 15},
        ],
    },
    {
        "code": "D",
        "text": "Clothing coverage when outdoors:",
        "options": [
            {"label": "Arms & lower legs exposed (short sleeves/shorts/dress)", "score": 0},
            {"label": "Long sleeves OR long pants (one area covered)", "score": 6},
            {"label": "Long sleeves AND long pants, head covering/veil", "score": 10},
        ],
    },
    {
        "code": "E1",
        "text": "Vitamin D supplement (≥ 600 IU / 15 µg most days):",
        "options": [
            {"label": "Yes", "score": -10},
            {"label": "No", "score": 0},
        ],
    },
    {
        "code": "E2",
        "text": "Vitamin D–rich foods ≥ 4 servings/week (oily fish, fortified milk/margarine, eggs):",
        "options": [
            {"label": "Yes", "score": -5},
            {"label": "No / rare", "score": 0},
        ],
    },
]

def score_total(answers):
    """answers is a list of option indices matching QUESTIONNAIRE order"""
    total = 0
    for i, opt_index in enumerate(answers):
        if opt_index is None:
            continue
        total += QUESTIONNAIRE[i]["options"][opt_index]["score"]
    return total

def classify(total):
    # tune cutoffs later if team adjusts
    if total <= 15:
        return "Adequate"
    elif total <= 35:
        return "Borderline"
    return "Inadequate"
