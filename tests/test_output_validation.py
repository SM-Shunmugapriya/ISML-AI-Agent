import pytest
from pydantic import ValidationError
from unittest.mock import patch

from services.output_schema import FinalOutput
from agents.output_validation import validate_final_output


def test_valid_final_output():
    data = {
        "topic": "Python",
        "recommendedResources": [
            {
                "title": "Python Course",
                "type": "Course",
                "qualityScore": 90.0,
                "difficulty": "Beginner",
                "category": "Programming",
                "summary": "Python basics course",
                "url": "https://example.com/python",
            }
        ],
        "learningSequence": [],
    }

    result = FinalOutput.model_validate(data)

    assert result.topic == "Python"
    assert len(result.recommendedResources) == 1


def test_missing_required_fields_rejected():
    data = {
        "topic": "Python",
        "recommendedResources": [
            {
                "title": "Python Course",
            }
        ],
        "learningSequence": [],
    }

    with pytest.raises(ValidationError):
        FinalOutput.model_validate(data)


def test_empty_required_fields_rejected():
    data = {
        "topic": "Python",
        "recommendedResources": [
            {
                "title": "Python Course",
                "type": "",
                "qualityScore": 80.0,
                "difficulty": "",
                "category": "",
                "summary": "",
                "url": "",
            }
        ],
        "learningSequence": [],
    }

    with pytest.raises(ValidationError):
        FinalOutput.model_validate(data)


def test_quality_score_range():
    data = {
        "topic": "Python",
        "recommendedResources": [
            {
                "title": "Python Course",
                "type": "Course",
                "qualityScore": 101.0,
                "difficulty": "Beginner",
                "category": "Programming",
                "summary": "Python basics",
                "url": "https://example.com/python",
            }
        ],
        "learningSequence": [],
    }

    with pytest.raises(ValidationError):
        FinalOutput.model_validate(data)


def test_invalid_output_triggers_repair():
    state = {
        "topic": "Python",
        "categorized_resources": [
            {
                "title": "Python Course",
                "type": "Course",
                "overall_score": 8.0,
                "difficulty": "Beginner",
                "category": "Programming",
                "summary": "Python basics course",
                "url": "https://example.com/python",
            }
        ],
        "learning_sequence": [],
        "validated_output": {},
    }

    repaired_output = {
        "topic": "Python",
        "recommendedResources": [
            {
                "title": "Python Course",
                "type": "Course",
                "qualityScore": 80.0,
                "difficulty": "Beginner",
                "category": "Programming",
                "summary": "Python basics course",
                "url": "https://example.com/python",
            }
        ],
        "learningSequence": [],
    }

    with patch(
        "agents.output_validation.repair_output",
        return_value=repaired_output,
    ) as mock_repair:

        result = validate_final_output(state)

        mock_repair.assert_not_called()
        assert result["validated_output"]["topic"] == "Python"
