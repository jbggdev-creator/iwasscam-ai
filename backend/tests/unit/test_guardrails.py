import pytest
from app.core.guardrails import sanitize_explanation


class TestSanitizeExplanation:
    def test_clean_text_unchanged(self):
        text = "This message shows suspicious patterns consistent with job scams."
        assert sanitize_explanation(text) == text

    def test_replaces_definitely_scam(self):
        result = sanitize_explanation("This is definitely a scam targeting job seekers.")
        assert "definitely" not in result.lower()
        assert "strong signs" in result

    def test_replaces_certainly_scam(self):
        result = sanitize_explanation("This is certainly a scam.")
        assert "strong signs" in result

    def test_replaces_absolutely_scam(self):
        result = sanitize_explanation("This is absolutely a scam.")
        assert "strong signs" in result

    def test_replaces_confirmed_fraud(self):
        result = sanitize_explanation("Confirmed fraud detected in this message.")
        assert "likely fraud" in result

    def test_replaces_guaranteed_scam(self):
        result = sanitize_explanation("guaranteed scam involving GCash transfers.")
        assert "likely scam" in result

    def test_replaces_guaranteed_fake(self):
        result = sanitize_explanation("This receipt is guaranteed fake.")
        assert "likely fake" in result

    def test_replaces_they_are_definitely_scamming(self):
        result = sanitize_explanation("They are definitely scamming you.")
        assert "suspicious activity" in result

    def test_replaces_conclusively_fraudulent(self):
        result = sanitize_explanation("This was conclusively fraudulent.")
        assert "appears fraudulent" in result

    def test_case_insensitive(self):
        result = sanitize_explanation("THIS IS DEFINITELY A SCAM.")
        assert "strong signs" in result.lower()

    def test_multiple_replacements_in_one_string(self):
        text = "This is definitely a scam. Confirmed fraud."
        result = sanitize_explanation(text)
        assert "strong signs" in result
        assert "likely fraud" in result

    def test_empty_string_unchanged(self):
        assert sanitize_explanation("") == ""
