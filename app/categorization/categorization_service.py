from typing import Dict


CATEGORIES = [
    "Core Learning",
    "Foundation",
    "Practice",
    "Revision",
    "Pronunciation",
    "Grammar",
    "Vocabulary",
    "Listening",
    "Speaking",
    "Assessment",
    "Supplementary",
]


CATEGORY_KEYWORDS: Dict[str, list[str]] = {
    "Pronunciation": ["pronunciation", "pronounce", "phonetic", "ipa", "sound"],
    "Grammar": ["grammar", "tense", "verb", "noun", "adjective", "sentence structure"],
    "Vocabulary": ["vocabulary", "word", "words", "meaning", "synonym", "antonym"],
    "Listening": ["listening", "audio", "listen", "comprehension"],
    "Speaking": ["speaking", "conversation", "speak", "dialogue", "communication"],
    "Practice": ["practice", "exercise", "quiz", "activity", "questions"],
    "Revision": ["revision", "revise", "review", "recap", "summary"],
    "Assessment": ["assessment", "test", "exam", "evaluation", "score"],
    "Foundation": ["basics", "basic", "introduction", "beginner", "fundamentals"],
    "Core Learning": ["tutorial", "lesson", "course", "learning", "concept"],
    "Supplementary": ["additional", "extra", "reference", "supplementary", "resource"],
}


def categorize_resource(
    metadata: Dict[str, str],
    content_snippet: str,
) -> Dict[str, object]:
    """
    Categorize a learning resource using its metadata and content snippet.

    Returns:
        {
            "category": <category name>,
            "confidence": <0.0 - 1.0>
        }
    """

    text_parts = [
        str(value)
        for value in metadata.values()
        if value is not None
    ]
    text_parts.append(content_snippet or "")

    text = " ".join(text_parts).lower()

    scores = {
        category: 0
        for category in CATEGORIES
    }

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text:
                scores[category] += 1

    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]

    if best_score == 0:
        return {
            "category": "Supplementary",
            "confidence": 0.30,
        }

    total_score = sum(scores.values())
    confidence = min(best_score / total_score, 1.0)

    return {
        "category": best_category,
        "confidence": round(confidence, 2),
    }