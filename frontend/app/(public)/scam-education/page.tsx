import type { Metadata } from "next";
import Link from "next/link";
import { AlertTriangle, ShieldCheck, ExternalLink } from "lucide-react";

export const metadata: Metadata = {
  title: "Scam Education — IwasScam AI",
  description: "Learn to recognize common online scams in the Philippines: GCash fraud, fake jobs, phishing, investment scams, and more.",
};

const SCAM_TYPES = [
  {
    title: "Job Recruitment Scams",
    severity: "high",
    summary: "Fake employers charge placement or training fees before you start work.",
    redFlags: [
      "Asked to pay a fee before your first day",
      "Job offer arrived via Facebook or text with no formal interview",
      "Salary is unusually high for minimal qualifications",
      "Employer contacts you first, unprompted",
      "No company website or verifiable address",
    ],
    whatToDo:
      "Legitimate employers NEVER ask you to pay to be hired. Report to DOLE or DMW if an overseas recruiter asks for placement fees.",
  },
  {
    title: "GCash / E-Wallet Scams",
    severity: "critical",
    summary: "Scammers impersonate GCash or ask you to receive and forward funds as a 'job.'",
    redFlags: [
      "Received a GCash request from an unknown number",
      "Asked to be a 'loading agent' or receive funds for a commission",
      "GCash 'support' messaging you to verify your account",
      "Link asks for your GCash MPIN or OTP",
      "Winning prize requires sending money first",
    ],
    whatToDo:
      "GCash will NEVER ask for your MPIN or OTP. Never receive and forward funds for strangers — you become a money mule and can face criminal charges.",
  },
  {
    title: "Fake Investment / Ponzi Schemes",
    severity: "critical",
    summary: "Promises of 30–100% monthly returns that pay early investors with new member funds.",
    redFlags: [
      "Guaranteed high returns with no risk",
      "Pressure to recruit others to earn more",
      "Investment 'opportunity' shared in Facebook groups",
      "Company not registered with SEC Philippines",
      "Payouts slow down or stop without explanation",
    ],
    whatToDo:
      "Always verify at sec.gov.ph before investing. No legitimate investment guarantees fixed returns. Report unregistered schemes to the SEC.",
  },
  {
    title: "Phishing Websites & Emails",
    severity: "high",
    summary: "Fake login pages that steal your banking credentials or personal information.",
    redFlags: [
      "URL looks almost right but has a typo (e.g. gcas-h.com)",
      "Urgent email warning your account will be closed",
      "Login page requests your OTP immediately",
      "Suspicious TLD: .tk, .ml, .cf, or random domain",
      "Padlock is missing or shows a security warning",
    ],
    whatToDo:
      "Always type bank and wallet URLs manually. Never click links in SMS or email. Use IwasScam AI to scan any suspicious URL before entering credentials.",
  },
  {
    title: "Romance Scams",
    severity: "high",
    summary: "Fake romantic partners build trust over weeks before requesting money.",
    redFlags: [
      "Met on Facebook, dating app, or Messenger — very attractive profile",
      "Claims to be OFW, military, or working abroad",
      "Relationship moves extremely fast",
      "Eventually asks for money for an emergency or travel",
      "Refuses or makes excuses to video call",
    ],
    whatToDo:
      "Reverse-image search profile photos. Never send money to someone you have not met in person. Report to the PNP Anti-Cybercrime Group.",
  },
  {
    title: "OFW Placement Fraud",
    severity: "critical",
    summary: "Illegal recruiters charge massive fees and provide fake visas for overseas work.",
    redFlags: [
      "Recruiter not listed on DMW's verified agency list",
      "Asks for tens of thousands of pesos upfront",
      "Promises specific countries with unusually high salaries",
      "Work visa or contract looks unofficial",
      "No POEA/DMW job order number provided",
    ],
    whatToDo:
      "Verify agencies at dmw.gov.ph. DMW prohibits placement fee collection before deployment. Report fraud to the DMW legal division.",
  },
];

const severityClass: Record<string, string> = {
  critical: "bg-destructive/10 text-destructive border-destructive/20",
  high: "bg-amber-50 text-amber-700 border-amber-200",
};

const severityLabel: Record<string, string> = {
  critical: "Critical risk",
  high: "High risk",
};

export default function ScamEducationPage() {
  return (
    <main className="mx-auto max-w-4xl px-4 py-12 space-y-12">
      <header className="space-y-4">
        <div className="inline-flex items-center gap-2 rounded-full bg-destructive/10 px-4 py-1.5 text-sm font-medium text-destructive">
          <AlertTriangle className="h-4 w-4" aria-hidden />
          Know before you click
        </div>
        <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-foreground">
          Scam Education Guide
        </h1>
        <p className="text-muted-foreground leading-relaxed max-w-2xl">
          The most common scams targeting Filipinos — what they look like, the red flags to watch
          for, and what to do if you encounter one.
        </p>
      </header>

      <div className="space-y-8">
        {SCAM_TYPES.map(({ title, severity, summary, redFlags, whatToDo }) => (
          <article key={title} className="rounded-xl border border-border bg-card overflow-hidden">
            <div className="p-6 space-y-4">
              <div className="flex items-start justify-between gap-4 flex-wrap">
                <h2 className="text-lg font-bold text-foreground">{title}</h2>
                <span
                  className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${severityClass[severity]}`}
                >
                  {severityLabel[severity]}
                </span>
              </div>
              <p className="text-sm text-muted-foreground">{summary}</p>

              <div>
                <p className="text-xs font-semibold text-foreground uppercase tracking-wide mb-2">
                  Red flags
                </p>
                <ul className="space-y-1.5">
                  {redFlags.map((flag) => (
                    <li key={flag} className="flex items-start gap-2 text-sm text-muted-foreground">
                      <AlertTriangle className="h-3.5 w-3.5 text-amber-500 flex-shrink-0 mt-0.5" aria-hidden />
                      {flag}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="rounded-lg bg-primary/5 border border-primary/20 px-4 py-3">
                <p className="text-xs font-semibold text-primary uppercase tracking-wide mb-1">
                  What to do
                </p>
                <p className="text-sm text-foreground leading-relaxed">{whatToDo}</p>
              </div>
            </div>
          </article>
        ))}
      </div>

      <section className="rounded-xl border border-border bg-card p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-primary" aria-hidden />
            <p className="font-semibold text-foreground">Think you received a scam?</p>
          </div>
          <p className="text-sm text-muted-foreground">
            Scan it with IwasScam AI — free, instant, and explainable.
          </p>
        </div>
        <Link
          href="/scanner"
          className="flex-shrink-0 rounded-lg bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground hover:opacity-90 transition-opacity"
        >
          Scan Now
        </Link>
      </section>

      <section className="space-y-4">
        <h2 className="text-lg font-bold text-foreground">Official reporting channels</h2>
        <div className="grid sm:grid-cols-2 gap-3 text-sm">
          {[
            { label: "BSP Consumer Protection", href: "https://www.bsp.gov.ph" },
            { label: "SEC Philippines", href: "https://www.sec.gov.ph" },
            { label: "PNP Anti-Cybercrime Group", href: "https://acg.pnp.gov.ph" },
            { label: "DMW / POEA", href: "https://www.dmw.gov.ph" },
          ].map(({ label, href }) => (
            <a
              key={label}
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-between rounded-lg border border-border px-4 py-3 hover:bg-muted transition-colors text-foreground"
            >
              {label}
              <ExternalLink className="h-3.5 w-3.5 text-muted-foreground" aria-hidden />
            </a>
          ))}
        </div>
      </section>
    </main>
  );
}
