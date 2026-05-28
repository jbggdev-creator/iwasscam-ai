import re
from dataclasses import dataclass

# (regex_pattern, finding_type, description, severity, score)
_SE_PATTERNS: list[tuple[str, str, str, str, int]] = [
    (
        r"(?i)\b(bayad muna|advance payment|registration fee|membership fee|processing fee|reservation fee|downpayment|advance.*fee|magbayad.*muna|pabayad|onboarding fee|training fee|placement fee|application fee|hiring fee|need to pay|must pay|pay \d+|bayad ng \d+)\b",
        "upfront_payment_demand",
        "Requests payment before delivering goods or services — the most common Philippine scam pattern.",
        "critical",
        40,
    ),
    (
        r"(?i)\b(limited time|act now|expires today|mabilis na|agad na|ngayon din|today only|hurry|pag.*hindi.*agad|deadline.*today|ilang.*oras na lang)\b",
        "urgency_pressure",
        "Uses urgency tactics to prevent the target from thinking or verifying the offer.",
        "high",
        25,
    ),
    (
        r"(?i)\b(arrested|warrant of arrest|legal action|ikulong|ikukulong|prison|charges filed|court order|NBI.*case|estafa|filed.*complaint|mag.*file.*kaso)\b",
        "legal_fear_threat",
        "Threatens legal consequences to create fear and compel compliance — a common intimidation tactic.",
        "critical",
        35,
    ),
    (
        r"(?i)\b(nanalo ka|you won|you are a winner|napalad|cash prize|congratulations.*prize|lucky winner|lotto.*winner|swerteng|raffle.*won|prize.*claim)\b",
        "prize_lottery_claim",
        "Claims an unexpected prize or lottery win — the classic advance-fee scam setup.",
        "critical",
        40,
    ),
    (
        r"(?i)\b(work from home|wfh.*easy|no experience needed|earn \d+.*per (day|hour)|guaranteed income|passive income|madali.*pera|recruiter.*fee|recruiter.*pay|pay.*onboarding|hiring fee|placement fee|job.*application.*fee)\b",
        "fake_job_offer",
        "Job offer promises unusually high pay with no experience required — likely a job scam.",
        "high",
        30,
    ),
    (
        r"(?i)\b(BSP|Bangko Sentral|BangkoSentral|SEC Philippines|SSS official|GSIS|PhilHealth.*official|Pag-IBIG.*official|BIR.*agent|DICT.*grant|NBI.*clearance.*required|PCSO.*official)\b",
        "authority_impersonation",
        "Claims to represent a Philippine government agency — always verify through official channels.",
        "high",
        25,
    ),
    (
        r"(?i)\b(invest.*guarante[a-z]*|guarante[a-z]*.*(return[a-z]*|profit[a-z]*|earn[a-z]*)|double.*money|doubling.*investment|crypto.*(profit[a-z]*|guarante[a-z]*)|bitcoin.*earn[a-z]*|paluwagan.*guarante[a-z]*|network marketing.*guarante[a-z]*)\b",
        "investment_scam_signal",
        "Promises guaranteed investment returns — no legitimate investment can guarantee profits.",
        "high",
        30,
    ),
    (
        r"(?i)\b(OFW.*send money|abroad.*padala|mahal kita.*padala|online.*relationship.*money|met.*online.*borrow|magpadala.*pera.*online.*friend)\b",
        "romance_scam_signal",
        "Money request from someone met online — romance and OFW impersonation scams are common in the Philippines.",
        "high",
        30,
    ),
    (
        r"(?i)\b(gcash.*send|send gcash|padala.*gcash|gcash.*number.*bayad|paymaya.*transfer|maya.*send|gcash.*stranger|padala.*load)\b",
        "gcash_payment_request",
        "GCash payment request from an unverified source — confirm the recipient's identity before sending.",
        "medium",
        20,
    ),
    (
        r"(?i)\b(online.*seller.*meet.*up|facebook.*marketplace.*scam|cod.*bayad.*muna|seller.*advance.*payment|buyer.*gcash.*first|legit.*seller.*bayad)\b",
        "online_marketplace_fraud",
        "Online marketplace transaction with suspicious payment terms — common in buy-and-sell scams.",
        "medium",
        15,
    ),
]


@dataclass(frozen=True)
class SeDetectionResult:
    signals: list[dict]
    total_score: int
    risk_level: str
    confidence: float


def detect_social_engineering(scenario: str) -> SeDetectionResult:
    """Run all SE heuristic patterns against the scenario text."""
    signals: list[dict] = []
    total_score = 0
    seen_types: set[str] = set()

    for pattern, finding_type, description, severity, score in _SE_PATTERNS:
        if finding_type in seen_types:
            continue
        if re.search(pattern, scenario):
            signals.append(
                {
                    "finding_type": finding_type,
                    "description": description,
                    "severity": severity,
                }
            )
            total_score += score
            seen_types.add(finding_type)

    total_score = min(total_score, 100)

    if total_score >= 80:
        risk_level = "critical"
    elif total_score >= 60:
        risk_level = "high"
    elif total_score >= 30:
        risk_level = "medium"
    else:
        risk_level = "low"

    signal_count = len(signals)
    confidence = round(min(0.95, 0.45 + (signal_count * 0.1) + (total_score / 250)), 2)

    return SeDetectionResult(
        signals=signals,
        total_score=total_score,
        risk_level=risk_level,
        confidence=confidence,
    )
