import pytest

from app.agents.social_engineering_agent import SeDetectionResult, detect_social_engineering


def test_upfront_payment_detected():
    result = detect_social_engineering(
        "A recruiter told me to pay a registration fee of ₱500 before I can start the job."
    )
    types = {s["finding_type"] for s in result.signals}
    assert "upfront_payment_demand" in types
    assert result.total_score >= 30


def test_prize_claim_detected():
    result = detect_social_engineering(
        "I got a message saying 'Nanalo ka ng ₱50,000 cash prize! Claim now.'"
    )
    types = {s["finding_type"] for s in result.signals}
    assert "prize_lottery_claim" in types
    assert result.risk_level in ("medium", "high", "critical")


def test_urgency_pressure_detected():
    result = detect_social_engineering(
        "They said the offer expires today and I need to act now or lose the deal."
    )
    types = {s["finding_type"] for s in result.signals}
    assert "urgency_pressure" in types


def test_legal_threat_detected():
    result = detect_social_engineering(
        "Someone claiming to be from the NBI said a warrant of arrest was filed against me for estafa."
    )
    types = {s["finding_type"] for s in result.signals}
    assert "legal_fear_threat" in types
    assert result.total_score >= 35


def test_gcash_request_detected():
    result = detect_social_engineering(
        "A stranger asked me to send gcash to this number: 09xxxxxxxxx."
    )
    types = {s["finding_type"] for s in result.signals}
    assert "gcash_payment_request" in types


def test_investment_scam_detected():
    result = detect_social_engineering(
        "They promised guaranteed return of 50% monthly from their crypto trading bot."
    )
    types = {s["finding_type"] for s in result.signals}
    assert "investment_scam_signal" in types


def test_clean_scenario_low_risk():
    result = detect_social_engineering(
        "I want to buy a second-hand phone from a friend. They said I can inspect it first."
    )
    assert result.risk_level == "low"
    assert result.total_score < 30


def test_multiple_signals_stack():
    result = detect_social_engineering(
        "I won a prize! But I need to pay a processing fee of ₱500 via gcash now, today only."
    )
    assert len(result.signals) >= 2
    assert result.total_score >= 60


def test_result_is_immutable():
    result = detect_social_engineering("test scenario")
    assert isinstance(result, SeDetectionResult)
    with pytest.raises(Exception):
        result.total_score = 999  # type: ignore[misc]


def test_confidence_bounded():
    result = detect_social_engineering(
        "Registration fee required! Prize won! Arrest warrant! Act now! Send gcash! "
        "Guaranteed investment returns! Work from home easy money!"
    )
    assert 0.0 <= result.confidence <= 1.0
    assert result.total_score <= 100


def test_risk_level_critical_threshold():
    result = detect_social_engineering(
        "You won a cash prize. Pay the processing fee of ₱500 via gcash now, bayad muna. "
        "Warrant of arrest will be filed if you don't act now."
    )
    assert result.risk_level == "critical"


@pytest.mark.parametrize("scenario,expected_type", [
    ("Work from home, no experience needed, easy money", "fake_job_offer"),
    ("OFW nurse abroad, mahal kita, send money please", "romance_scam_signal"),
    ("BSP official calling about your account", "authority_impersonation"),
])
def test_parametrized_pattern_detection(scenario: str, expected_type: str):
    result = detect_social_engineering(scenario)
    types = {s["finding_type"] for s in result.signals}
    assert expected_type in types


def test_job_scam_pay_amount_detected():
    result = detect_social_engineering(
        "A recruiter asked me to pay 500 pesos for onboarding before the interview starts."
    )
    types = {s["finding_type"] for s in result.signals}
    assert "upfront_payment_demand" in types or "fake_job_offer" in types
    assert result.risk_level in ("medium", "high", "critical")


def test_onboarding_fee_detected():
    result = detect_social_engineering(
        "The company requires an onboarding fee of ₱1500 before you can begin training."
    )
    types = {s["finding_type"] for s in result.signals}
    assert "upfront_payment_demand" in types


def test_training_fee_detected():
    result = detect_social_engineering(
        "Please pay the training fee before your first day at work."
    )
    types = {s["finding_type"] for s in result.signals}
    assert "upfront_payment_demand" in types


def test_placement_fee_detected():
    result = detect_social_engineering(
        "Our agency charges a placement fee of ₱3000 for domestic helpers."
    )
    types = {s["finding_type"] for s in result.signals}
    assert "upfront_payment_demand" in types or "fake_job_offer" in types


def test_recruiter_pay_fake_job_detected():
    result = detect_social_engineering(
        "Recruiter told me to pay ₱800 for the ID before I can start."
    )
    types = {s["finding_type"] for s in result.signals}
    assert "fake_job_offer" in types or "upfront_payment_demand" in types
