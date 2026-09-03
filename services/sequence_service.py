from typing import List, Dict, Any


CATEGORY_ORDER = {
    "Core Learning": 1,
    "Foundation": 2,
    "Grammar": 3,
    "Vocabulary": 4,
    "Pronunciation": 5,
    "Listening": 6,
    "Speaking": 7,
    "Practice": 8,
    "Revision": 9,
    "Assessment": 10,
    "Supplementary": 11,
}

DIFFICULTY_ORDER = {
    "beginner": 1,
    "basic": 1,
    "easy": 1,
    "intermediate": 2,
    "medium": 2,
    "advanced": 3,
    "hard": 3,
}


def generate_learning_sequence(
    resources: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Generate an ordered learning path with a maximum of 10 steps."""

    if not resources:
        return []

    sorted_resources = sorted(
        resources,
        key=lambda resource: (
            CATEGORY_ORDER.get(
                resource.get("category", "Supplementary"),
                11,
            ),
            DIFFICULTY_ORDER.get(
                str(resource.get("difficulty", "beginner")).lower(),
                2,
            ),
            resource.get("rank", 9999),
        ),
    )

    # Maximum 10 steps
    selected_resources = sorted_resources[:10]

    learning_sequence = []

    for index, resource in enumerate(selected_resources, start=1):
        learning_sequence.append({
            **resource,
            "learning_order": index,
        })

    return learning_sequence