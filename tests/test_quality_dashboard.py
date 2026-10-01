from services.quality_config import get_quality_level


def test_quality_levels():
    assert get_quality_level(95) == "Excellent"
    assert get_quality_level(85) == "High Quality"
    assert get_quality_level(75) == "Acceptable"
    assert get_quality_level(65) == "Review/Reject"
