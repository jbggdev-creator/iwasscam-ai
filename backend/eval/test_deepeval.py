"""
DeepEval eval harness for IwasScam AI.

Run with:
    pytest eval/ -m eval -v

Requires:
    uv pip install -e ".[eval]"
    export OPENAI_API_KEY=sk-...   # DeepEval uses GPT-4 for LLM-as-judge metrics
"""

import pytest

pytest.importorskip("deepeval", reason="deepeval not installed; run: uv pip install -e '.[eval]'")

from deepeval import assert_test  # noqa: E402
from deepeval.metrics import AnswerRelevancyMetric  # noqa: E402
from deepeval.test_case import LLMTestCase  # noqa: E402

from app.agents.social_engineering_agent import detect_social_engineering  # noqa: E402
from app.core.guardrails import sanitize_explanation  # noqa: E402
from eval.dataset import SCAM_ONLY_CASES, SAFE_CASES  # noqa: E402

pytestmark = pytest.mark.eval


class TestGuardrailsOnGoldenDataset:
    """Guardrail must not produce definitive accusation language on any golden case."""

    _DEFINITIVE_PHRASES = [
        "this is definitely a scam",
        "this is certainly a scam",
        "confirmed fraud",
        "guaranteed scam",
        "guaranteed fraud",
    ]

    @pytest.mark.parametrize("case", SCAM_ONLY_CASES, ids=lambda c: c.expected_risk_level)
    def test_no_definitive_phrases(self, case):
        sanitized = sanitize_explanation(case.scenario)
        for phrase in self._DEFINITIVE_PHRASES:
            assert phrase.lower() not in sanitized.lower(), (
                f"Definitive phrase '{phrase}' found for: {case.scenario[:60]}"
            )


class TestSocialEngineeringOnGoldenDataset:
    """SE detector must classify safe scenarios as low-risk."""

    @pytest.mark.parametrize("case", SAFE_CASES, ids=lambda c: c.scenario[:30])
    def test_safe_scenario_low_score(self, case):
        result = detect_social_engineering(case.scenario)
        assert result.total_score < 30, (
            f"Safe scenario scored {result.total_score} (expected < 30): {case.scenario[:60]}"
        )

    @pytest.mark.parametrize("case", SCAM_ONLY_CASES, ids=lambda c: c.expected_risk_level)
    def test_scam_scenario_nonzero_score(self, case):
        result = detect_social_engineering(case.scenario)
        assert result.total_score > 0, (
            f"Scam scenario scored 0: {case.scenario[:60]}"
        )


class TestAnswerRelevancy:
    """DeepEval LLM-as-judge: explanations must be relevant to the input."""

    @pytest.mark.parametrize("case", SCAM_ONLY_CASES[:2], ids=lambda c: c.expected_risk_level)
    def test_explanation_relevancy(self, case):
        result = detect_social_engineering(case.scenario)
        signal_desc = result.signals[0]["description"] if result.signals else "No signals found."
        explanation = (
            f"Detected {len(result.signals)} social engineering signal(s). "
            f"Risk score: {result.total_score}. {signal_desc}"
        )

        test_case = LLMTestCase(input=case.scenario, actual_output=explanation)
        assert_test(test_case, [AnswerRelevancyMetric(threshold=0.5)])
