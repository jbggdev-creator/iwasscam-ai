import type { Metadata } from "next";
import Link from "next/link";
import { CheckCircle, ShieldCheck } from "lucide-react";

export const metadata: Metadata = {
  title: "Pricing — IwasScam AI",
  description: "IwasScam AI is free to use. Scan URLs, screenshots, QR codes, and scenarios at no cost.",
};

const FREE_FEATURES = [
  "URL scans — unlimited",
  "Screenshot & image analysis",
  "QR code decoding and analysis",
  "Ask AI scenario analysis",
  "Scan history (last 20 scans)",
  "Explainable risk scores and findings",
  "Philippine fraud intelligence RAG",
];

const COMING_SOON = [
  "Unlimited scan history",
  "Save and export scan reports",
  "Batch URL scanning",
  "API access for developers",
  "Priority analysis queue",
  "Advanced phishing intelligence",
];

export default function PricingPage() {
  return (
    <main className="mx-auto max-w-4xl px-4 py-12 space-y-12">
      <header className="text-center space-y-4 max-w-xl mx-auto">
        <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-foreground">
          Simple, honest pricing
        </h1>
        <p className="text-muted-foreground leading-relaxed">
          Protecting yourself from scams should never cost money. IwasScam AI is free to use —
          no credit card, no sign-up required to scan.
        </p>
      </header>

      <div className="grid sm:grid-cols-2 gap-6 max-w-3xl mx-auto">
        <div className="rounded-2xl border-2 border-primary bg-card p-7 space-y-6 relative">
          <div className="absolute -top-3 left-6">
            <span className="bg-primary text-primary-foreground text-xs font-semibold px-3 py-1 rounded-full">
              Available now
            </span>
          </div>
          <div className="space-y-1">
            <h2 className="text-xl font-bold text-foreground">Free</h2>
            <div className="flex items-end gap-1">
              <span className="text-4xl font-bold text-foreground">₱0</span>
              <span className="text-muted-foreground text-sm mb-1">/ forever</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Full scam detection — no account required to scan.
            </p>
          </div>
          <ul className="space-y-2.5">
            {FREE_FEATURES.map((f) => (
              <li key={f} className="flex items-center gap-2.5 text-sm text-foreground">
                <CheckCircle className="h-4 w-4 text-primary flex-shrink-0" aria-hidden />
                {f}
              </li>
            ))}
          </ul>
          <Link
            href="/scanner"
            className="block w-full rounded-lg bg-primary py-2.5 text-center text-sm font-semibold text-primary-foreground hover:opacity-90 transition-opacity"
          >
            Start Scanning Free
          </Link>
        </div>

        <div className="rounded-2xl border border-border bg-muted/30 p-7 space-y-6 relative opacity-75">
          <div className="absolute -top-3 left-6">
            <span className="bg-muted text-muted-foreground text-xs font-semibold px-3 py-1 rounded-full border border-border">
              Coming soon
            </span>
          </div>
          <div className="space-y-1">
            <h2 className="text-xl font-bold text-foreground">Pro</h2>
            <div className="flex items-end gap-1">
              <span className="text-4xl font-bold text-muted-foreground">TBA</span>
            </div>
            <p className="text-sm text-muted-foreground">
              For power users, developers, and security teams.
            </p>
          </div>
          <ul className="space-y-2.5">
            <li className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Everything in Free, plus:
            </li>
            {COMING_SOON.map((f) => (
              <li key={f} className="flex items-center gap-2.5 text-sm text-muted-foreground">
                <CheckCircle className="h-4 w-4 text-muted-foreground/50 flex-shrink-0" aria-hidden />
                {f}
              </li>
            ))}
          </ul>
          <button
            disabled
            className="block w-full rounded-lg border border-border py-2.5 text-center text-sm font-semibold text-muted-foreground cursor-not-allowed"
          >
            Notify me when available
          </button>
        </div>
      </div>

      <section className="rounded-xl bg-muted/30 border border-border px-6 py-6 max-w-2xl mx-auto text-center space-y-3">
        <div className="flex items-center justify-center gap-2">
          <ShieldCheck className="h-5 w-5 text-primary" aria-hidden />
          <h2 className="font-semibold text-foreground">Our commitment</h2>
        </div>
        <p className="text-sm text-muted-foreground leading-relaxed">
          Core scam detection will always be free. We believe every Filipino deserves access to
          fraud protection tools regardless of income. A Pro tier will only add convenience
          features — never gate the core safety functionality.
        </p>
      </section>
    </main>
  );
}
