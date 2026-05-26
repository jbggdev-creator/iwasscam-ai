"""
Philippine scam knowledge base seed data.
Run: python -m app.data.seed_knowledge
"""
import asyncio
import logging

logger = logging.getLogger(__name__)

SEED_DOCUMENTS: list[dict] = [
    {
        "source": "BSP Advisory — GCash Money Mule Scam",
        "content": (
            "Scammers recruit victims to receive money via GCash and forward it to another account, "
            "keeping a small commission. They often pose as employers offering easy work-from-home "
            "jobs. Victims unknowingly become money mules and can face criminal charges. BSP and "
            "GCash will never ask you to receive and forward funds for strangers."
        ),
        "metadata": {"type": "gcash_scam", "severity": "high", "source_type": "bsp_advisory"},
    },
    {
        "source": "SEC Philippines — Fake Investment / Ponzi Scheme",
        "content": (
            "Fraudulent investment schemes promise high returns (30–100% monthly) with minimal risk. "
            "Operators recruit new investors to pay earlier ones (Ponzi structure). Common in the "
            "Philippines: paluwagan fraud, crypto investment scams, and MLM pyramid schemes. "
            "SEC-registered companies never guarantee fixed returns. Always verify registration "
            "at sec.gov.ph before investing."
        ),
        "metadata": {"type": "investment_scam", "severity": "high", "source_type": "sec_advisory"},
    },
    {
        "source": "DICT Alert — Fake Job Recruitment Scam",
        "content": (
            "Job scammers post fake work-from-home or online job ads promising high hourly pay "
            "with no experience required. They charge a placement fee, training fee, or ID "
            "processing fee before the victim starts. Legitimate employers never ask candidates "
            "to pay fees. Victims lose the fee and never receive any employment."
        ),
        "metadata": {"type": "job_scam", "severity": "high", "source_type": "dict_alert"},
    },
    {
        "source": "PNP ACG — Online Romance / OFW Impersonation Scam",
        "content": (
            "Scammers build romantic relationships online over weeks or months, then request money "
            "via GCash or remittance citing emergencies (medical, travel, customs fees). They often "
            "pose as OFW nurses, military officers, or engineers working abroad. Once money is sent, "
            "they disappear. The PNP Anti-Cybercrime Group warns: never send money to someone you "
            "have not met in person."
        ),
        "metadata": {"type": "romance_scam", "severity": "high", "source_type": "pnp_advisory"},
    },
    {
        "source": "BSP Advisory — Fake Prize / Lottery Notification",
        "content": (
            "Victims receive SMS, email, or Facebook messages claiming they won a cash prize, "
            "raffle, or government grant. To claim the prize, they must pay a processing fee or "
            "release fee via GCash. No legitimate lottery requires winners to pay fees upfront. "
            "PCSO will never contact winners through social media."
        ),
        "metadata": {"type": "prize_scam", "severity": "critical", "source_type": "bsp_advisory"},
    },
    {
        "source": "NBI Cybercrime Division — Legal Threat / Warrant Intimidation Scam",
        "content": (
            "Scammers impersonate NBI agents or court officials claiming a warrant of arrest has "
            "been issued for cyber libel, estafa, or drug charges. Victims are asked to pay bail "
            "or settlement via GCash to avoid arrest. The NBI and courts never demand payment via "
            "GCash. Always verify any legal threat directly with the NBI hotline."
        ),
        "metadata": {"type": "legal_threat_scam", "severity": "critical", "source_type": "nbi_advisory"},
    },
    {
        "source": "DTI Philippines — Facebook Marketplace COD Fraud",
        "content": (
            "Online sellers on Facebook Marketplace accept orders with Cash on Delivery payment "
            "but ship empty boxes or broken items. Some ask buyers to pay a partial GCash deposit "
            "before shipment. DTI advises buyers to transact only with verified sellers and avoid "
            "paying advance deposits for COD orders."
        ),
        "metadata": {"type": "online_selling_scam", "severity": "medium", "source_type": "dti_advisory"},
    },
    {
        "source": "BSP Advisory — Phishing SMS / Smishing Attack",
        "content": (
            "Phishing SMS messages impersonate banks, GCash, Maya, or government agencies. They "
            "claim the recipient's account will be suspended and provide a fake link to verify "
            "account details. Entering credentials on the fake site gives scammers full account "
            "access. Legitimate banks and e-wallets never ask for OTP or passwords via SMS."
        ),
        "metadata": {"type": "phishing_smishing", "severity": "critical", "source_type": "bsp_advisory"},
    },
    {
        "source": "SEC Philippines — Cryptocurrency Investment Scam",
        "content": (
            "Crypto scams promise high daily returns from automated trading bots or DeFi protocols. "
            "Scammers use celebrity endorsements, fabricated earnings screenshots, and referral "
            "bonuses to recruit victims. Withdrawals are blocked once a large enough deposit is "
            "made. SEC warns: no crypto platform can legally guarantee returns without SEC "
            "registration."
        ),
        "metadata": {"type": "crypto_scam", "severity": "high", "source_type": "sec_advisory"},
    },
    {
        "source": "DICT Alert — Government Grant / Cash Assistance Scam",
        "content": (
            "Scammers impersonate DSWD, DICT, or other agencies offering cash assistance grants "
            "via Facebook or SMS. Victims must pay a processing or courier fee to receive the "
            "grant. Real government cash assistance programs are applied through official channels "
            "and never require payment from recipients."
        ),
        "metadata": {"type": "government_grant_scam", "severity": "high", "source_type": "dict_alert"},
    },
    {
        "source": "PNP ACG — Online Lending App Extortion",
        "content": (
            "Illegitimate online lending apps access contacts and gallery then harass borrowers "
            "with threatening messages and doctored images when repayment is overdue. SEC has "
            "ordered the shutdown of dozens of such apps. Only borrow from SEC-registered "
            "lending platforms verified at sec.gov.ph."
        ),
        "metadata": {"type": "lending_harassment", "severity": "high", "source_type": "pnp_advisory"},
    },
    {
        "source": "BSP Advisory — Fake Travel Agency Scam",
        "content": (
            "Fake travel agencies advertise extremely cheap tour packages on Facebook. Victims "
            "pay full tour fees upfront via GCash or bank transfer. The agency stops responding "
            "after payment or provides fake booking confirmations. Always verify travel agencies "
            "with DOT accreditation and pay via credit card for chargeback protection."
        ),
        "metadata": {"type": "travel_scam", "severity": "medium", "source_type": "bsp_advisory"},
    },
    {
        "source": "DICT Alert — SIM Registration Identity Theft",
        "content": (
            "Following the SIM Registration Act, scammers send messages claiming the recipient's "
            "SIM will be deactivated unless they verify details through a link. The link harvests "
            "ID photos and personal information for identity theft. The NTC only accepts SIM "
            "registration through official telco portals."
        ),
        "metadata": {"type": "identity_theft", "severity": "high", "source_type": "dict_alert"},
    },
    {
        "source": "SEC Philippines — Paluwagan / Informal Investment Fraud",
        "content": (
            "Traditional paluwagan are increasingly used as cover for fraud. Organizers collect "
            "weekly contributions but disappear before distributing funds, or claim earlier "
            "members were paid to build trust. Online paluwagan groups with strangers are "
            "high-risk. Only participate in groups with known, trusted members."
        ),
        "metadata": {"type": "paluwagan_fraud", "severity": "high", "source_type": "sec_advisory"},
    },
    {
        "source": "PNP ACG — Fake Overseas Recruiter Placement Fee Scam",
        "content": (
            "Fake recruitment agencies for overseas jobs advertise on Facebook and job boards. "
            "They charge placement fees of tens of thousands of pesos, then either disappear or "
            "provide fraudulent work visas. DMW prohibits collection of placement fees before "
            "deployment. Verify agencies at dmw.gov.ph before paying any fees."
        ),
        "metadata": {"type": "recruitment_scam", "severity": "critical", "source_type": "pnp_advisory"},
    },
]


async def run_seed(db_session=None) -> int:
    """Ingest seed documents. Returns count added (0 if already seeded)."""
    from app.db.repositories.rag_repo import rag_repo
    from app.db.session import async_session_factory
    from app.services.rag_service import rag_service

    async with (db_session or async_session_factory()) as db:
        existing = await rag_repo.count(db)
        if existing >= len(SEED_DOCUMENTS):
            logger.info("Knowledge base already seeded (%d documents). Skipping.", existing)
            return 0

        added = 0
        for doc in SEED_DOCUMENTS:
            await rag_service.ingest(
                db,
                source=doc["source"],
                content=doc["content"],
                metadata=doc["metadata"],
            )
            added += 1
            logger.info("Seeded: %s", doc["source"])

        logger.info("Seeded %d documents into the RAG knowledge base.", added)
        return added


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_seed())
