"""Golden dataset of Philippine scam scenarios for the eval harness."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ScamCase:
    scenario: str
    expected_risk_level: str   # "low" | "medium" | "high" | "critical"
    expected_findings: tuple[str, ...]
    is_scam: bool


SCAM_CASES: list[ScamCase] = [
    ScamCase(
        scenario=(
            "A recruiter from JobsNow PH messaged me on Facebook. They said I got the job "
            "but must pay ₱1,500 registration fee via GCash before my start date next week."
        ),
        expected_risk_level="high",
        expected_findings=("upfront_payment_demand", "fake_job_offer"),
        is_scam=True,
    ),
    ScamCase(
        scenario=(
            "Someone texted me saying I won ₱50,000 in a Smart load promo. "
            "To claim the prize I need to send ₱200 processing fee first."
        ),
        expected_risk_level="high",
        expected_findings=("prize_scam", "upfront_payment_demand"),
        is_scam=True,
    ),
    ScamCase(
        scenario=(
            "I received a message from someone claiming to be an NBI agent. "
            "They said I have a warrant and must pay ₱5,000 via GCash to avoid arrest."
        ),
        expected_risk_level="critical",
        expected_findings=("authority_impersonation", "upfront_payment_demand"),
        is_scam=True,
    ),
    ScamCase(
        scenario=(
            "An online seller on Shopee is asking me to pay via bank transfer instead of "
            "Shopee's checkout. They claim Shopee checkout is down and this is faster."
        ),
        expected_risk_level="medium",
        expected_findings=("marketplace_fraud",),
        is_scam=True,
    ),
    ScamCase(
        scenario=(
            "My employer sent me a payslip via email with my salary breakdown for the month. "
            "I received it every 15th and 30th as usual."
        ),
        expected_risk_level="low",
        expected_findings=(),
        is_scam=False,
    ),
]

SAFE_CASES: list[ScamCase] = [c for c in SCAM_CASES if not c.is_scam]
SCAM_ONLY_CASES: list[ScamCase] = [c for c in SCAM_CASES if c.is_scam]
