import type { Metadata } from "next";
import Link from "next/link";
import {
  Link2,
  ImageIcon,
  QrCode,
  MessageSquare,
  ShieldCheck,
  Brain,
  Database,
  Zap,
  Lock,
} from "lucide-react";

export const metadata: Metadata = {
  title: "Features — IwasScam AI",
  description: "AI-powered scam detection features: URL analysis, screenshot OCR, QR scanning, and social engineering detection for Filipinos.",
};

const SCAN_FEATURES = [
  {
    icon: Link2,
    title: "URL Intelligence",
    badge: "Real-time",
    points: [
      "WHOIS domain age — new domains are a major red flag",
      "SSL/TLS certificate validity check",
      "Suspicious TLD detection (.tk, .ml, .cf, .xyz, etc.)",
      "Redirect chain analysis (up to 10 hops)",
      "URL entropy scoring for auto-generated phishing links",
    ],
  },
  {
    icon: ImageIcon,
    title: "Screenshot Analysis",
    badge: "OCR-powered",
    points: [
      "Optical character recognition on any uploaded image",
      "Fake GCash receipt detection",
      "Suspicious Messenger and Facebook Marketplace chat patterns",
      "Urgency language and manipulation tactic detection",
      "Supports JPEG, PNG, and WebP up to 10 MB",
    ],
  },
  {
    icon: QrCode,
    title: "QR Code Analysis",
    badge: "Decode & verify",
    points: [
      "Decodes QR code content from any image",
      "Follows decoded URLs through the full URL intelligence pipeline",
      "Detects QR codes that redirect to phishing pages",
      "Flags QR codes with suspicious encoded payloads",
    ],
  },
  {
    icon: MessageSquare,
    title: "Scenario Analysis",
    badge: "Social engineering",
    points: [
      "Detects urgency and fear manipulation tactics",
      "Identifies fake authority impersonation patterns",
      "Upfront payment demand detection",
      "Matched against Philippine RAG knowledge base",
      "Explains WHY something is suspicious in plain language",
    ],
  },
];

const AI_FEATURES = [
  {
    icon: Brain,
    title: "Explainable AI",
    description:
      "Every verdict comes with specific, evidence-backed reasons — not just a score. You'll know exactly which signals triggered the warning.",
  },
  {
    icon: Database,
    title: "Philippine RAG Knowledge Base",
    description:
      "Retrieval-augmented generation grounded in BSP, SEC, DICT, PNP, and DMW advisories. AI answers are anchored to real fraud intelligence, not hallucinations.",
  },
  {
    icon: Zap,
    title: "Sub-10-second Analysis",
    description:
      "URL scans complete in under 5 seconds. Text and image analysis under 10 seconds. Fast enough to check before you click.",
  },
  {
    icon: Lock,
    title: "Privacy-first Design",
    description:
      "Uploaded images are processed and discarded — never permanently stored. Your screenshots don't live on our servers.",
  },
];

export default function FeaturesPage() {
  return (
    <main className="mx-auto max-w-6xl px-4 py-12 space-y-16">
      <header className="text-center space-y-4 max-w-2xl mx-auto">
        <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-foreground">
          Everything you need to spot a scam
        </h1>
        <p className="text-muted-foreground leading-relaxed">
          IwasScam AI combines real-time intelligence checks, OCR, and AI reasoning in a single
          platform built for the Philippine threat landscape.
        </p>
      </header>

      <section className="space-y-6">
        <h2 className="text-xl font-bold text-foreground">Scanning capabilities</h2>
        <div className="grid md:grid-cols-2 gap-6">
          {SCAN_FEATURES.map(({ icon: Icon, title, badge, points }) => (
            <div key={title} className="rounded-xl border border-border bg-card p-6 space-y-4">
              <div className="flex items-center gap-3">
                <div className="inline-flex rounded-lg bg-primary/10 p-2.5">
                  <Icon className="h-5 w-5 text-primary" aria-hidden />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground">{title}</h3>
                  <span className="text-xs font-medium text-primary bg-primary/10 rounded-full px-2 py-0.5">
                    {badge}
                  </span>
                </div>
              </div>
              <ul className="space-y-2">
                {points.map((p) => (
                  <li key={p} className="flex items-start gap-2 text-sm text-muted-foreground">
                    <ShieldCheck className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" aria-hidden />
                    {p}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      <section className="space-y-6">
        <h2 className="text-xl font-bold text-foreground">AI architecture</h2>
        <div className="grid sm:grid-cols-2 gap-5">
          {AI_FEATURES.map(({ icon: Icon, title, description }) => (
            <div key={title} className="rounded-xl border border-border bg-card p-5 space-y-2">
              <div className="flex items-center gap-2.5">
                <Icon className="h-5 w-5 text-primary" aria-hidden />
                <h3 className="font-semibold text-foreground">{title}</h3>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-2xl bg-primary px-8 py-10 text-center space-y-4">
        <h2 className="text-xl font-bold text-primary-foreground">Ready to scan?</h2>
        <p className="text-primary-foreground/80 text-sm">No account required.</p>
        <Link
          href="/scanner"
          className="inline-block rounded-lg bg-background px-8 py-3 text-sm font-semibold text-foreground hover:bg-background/90 transition-colors"
        >
          Open Scanner
        </Link>
      </section>
    </main>
  );
}
