from services.llm_service import ask_llm
from services.logger import log_info, log_warning


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


def categorize_resource(resource: dict, provider: str = "gemini") -> str:
    """
    Assign a pedagogical category to an academic resource.

    Uses resource metadata and LLM analysis.
    """

    title = resource.get("title", "")
    summary = resource.get("summary", "")
    keywords = resource.get("keywords", [])
    resource_type = resource.get("type", "")
    difficulty = resource.get("difficulty", "")

    if isinstance(keywords, list):
        keywords_text = ", ".join(str(k) for k in keywords)
    else:
        keywords_text = str(keywords)

    prompt = f"""
You are an academic resource categorization system.

Classify the following learning resource into exactly ONE
of the allowed pedagogical categories.

Allowed categories:
{", ".join(CATEGORIES)}

Resource metadata:

Title: {title}
Summary: {summary}
Keywords: {keywords_text}
Resource Type: {resource_type}
Difficulty: {difficulty}

Rules:
- Return ONLY one category name.
- Do not return explanations.
- Do not create a new category.
- Choose the category that best represents the primary learning purpose.
- If the resource is mainly a test, exam, quiz, assessment, mock test,
  or evaluation activity, choose Assessment.
- If the resource is mainly exercises or hands-on activities,
  choose Practice.
- If the resource is mainly reviewing previously learned material,
  choose Revision.
- If the resource teaches basic concepts for beginners,
  choose Foundation.
- If the resource teaches the main subject content,
  choose Core Learning.

Return only the category name.
"""

    log_info(
        f"Categorization started | title={title}"
    )

    try:
        response = ask_llm(prompt, provider=provider)

        if isinstance(response, dict):
            category = (
                response.get("category")
                or response.get("text")
                or response.get("response")
                or response.get("content")
            )
        else:
            category = response

        if category is None:
            raise ValueError("Empty categorization response")

        category = str(category).strip()

        # Exact category match
        for allowed_category in CATEGORIES:
            if category.lower() == allowed_category.lower():
                log_info(
                    f"Categorization successful | "
                    f"title={title} | category={allowed_category}"
                )
                return allowed_category

        # Handle accidental extra text from LLM
        category_lower = category.lower()

        for allowed_category in CATEGORIES:
            if allowed_category.lower() in category_lower:
                log_info(
                    f"Categorization normalized | "
                    f"title={title} | category={allowed_category}"
                )
                return allowed_category

        raise ValueError(
            f"Invalid category returned by LLM: {category}"
        )

    except Exception as e:
        log_warning(
            f"Categorization failed | "
            f"title={title} | error={e}"
        )

        # Safe deterministic fallback
        fallback_category = deterministic_category(resource)

        log_info(
            f"Categorization fallback | "
            f"title={title} | category={fallback_category}"
        )

        return fallback_category


def deterministic_category(resource: dict) -> str:
    """
    Keyword-based fallback categorization.

    Used when the LLM is unavailable or returns
    an invalid category.
    """

    title = str(resource.get("title", "")).lower()
    summary = str(resource.get("summary", "")).lower()
    keywords = resource.get("keywords", [])

    if isinstance(keywords, list):
        keywords_text = " ".join(
            str(k).lower() for k in keywords
        )
    else:
        keywords_text = str(keywords).lower()

    text = f"{title} {summary} {keywords_text}"

    # Assessment is intentionally checked first.
    # Example: "English Grammar Test" -> Assessment
    keyword_rules = {
        "Assessment": [
            "assessment",
            "test",
            "exam",
            "quiz",
            "mock test",
            "practice test",
            "evaluation",
        ],

        "Pronunciation": [
            "pronunciation",
            "phonetic",
            "phonetics",
            "ipa",
            "accent",
        ],

        "Listening": [
            "listening",
            "audio",
            "listen",
            "conversation audio",
        ],

        "Speaking": [
            "speaking",
            "conversation",
            "oral",
            "spoken english",
        ],

        "Grammar": [
            "grammar",
            "tense",
            "tenses",
            "noun",
            "verb",
            "adjective",
            "sentence structure",
        ],

        "Vocabulary": [
            "vocabulary",
            "words",
            "word list",
            "synonyms",
            "antonyms",
        ],

        "Revision": [
            "revision",
            "revise",
            "review",
            "recap",
        ],

        "Practice": [
            "practice",
            "exercise",
            "workbook",
            "worksheet",
            "drill",
        ],

        "Foundation": [
            "beginner",
            "basic",
            "basics",
            "fundamentals",
            "introduction",
            "introductory",
        ],

        "Core Learning": [
            "lesson",
            "course",
            "tutorial",
            "lecture",
            "learn",
            "learning",
        ],
    }

    for category, keywords_list in keyword_rules.items():
        for keyword in keywords_list:
            if keyword in text:
                return category

    # Default category when no specific purpose is detected
    return "Supplementary"