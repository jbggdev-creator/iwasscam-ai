import Link from "next/link";
import {
  ShieldCheck,
  Link2,
  ImageIcon,
  QrCode,
  MessageSquare,
  AlertTriangle,
  CheckCircle,
  BookOpen,
} from "lucide-react";

const FEATURES = [
  {
    icon: Link2,
    title: "URL Analysis",
    description:
      "Instant checks on domain age, SSL validity, suspicious TLDs, phishing databases, and redirect chains.",
  },
  {
    icon: ImageIcon,
    title: "Screenshot Analysis",
    description:
      "Upload GCash receipts, Messenger chats, or Facebook Marketplace screenshots for OCR-powered fraud detection.",
  },
  {
    icon: QrCode,
    title: "QR Code Scanning",
    description:
      "Decode QR codes and analyze their destinations for malicious redirects before you tap.",
  },
  {
    icon: MessageSquare,
    title: "Ask AI",
    description:
      "Describe any suspicious situation in plain Filipino or English — our AI identifies social engineering tactics instantly.",
  },
];

const HOW_IT_WORKS = [
  {
    step: "1",
    title: "Submit what you received",
    description: "Paste a URL, upload a screenshot, scan a QR code, or describe the situation.",
  },
  {
    step: "2",
    title: "AI analyzes for red flags",
    description:
      "Our LangGraph pipeline checks against Philippine fraud intelligence, domain data, and social engineering patterns.",
  },
  {
    step: "3",
    title: "Get a clear verdict",
    description:
      "Receive an explainable risk score, specific warning signs, and a plain-language recommendation.",
  },
];

const SCAM_TYPES = [
  "GCash money mule scams",
  "Fake job recruitment fees",
  "Phishing login pages",
  "Fake investment schemes",
  "OFW placement fraud",
  "Romance and love scams",
];

export default function LandingPage() {
  return (
    <main>
      {/* Hero */}
      <section className="mx-auto max-w-6xl px-4 pt-20 pb-16 text-center space-y-6">
        <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary">
          <ShieldCheck className="h-4 w-4" aria-hidden />
          Built for the Philippines
        </div>
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight text-foreground max-w-3xl mx-auto leading-tight">
          Stop scams before they stop you
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
          IwasScam AI uses multimodal AI and Philippine threat intelligence to analyze suspicious
          URLs, screenshots, QR codes, and scenarios — giving you an explainable risk score in
          seconds.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center pt-2">
          <Link
            href="/scanner"
            className="rounded-lg bg-primary px-8 py-3 text-sm font-semibold text-primary-foreground hover:opacity-90 transition-opacity"
          >
            Start Scanning Free
          </Link>
          <Link
            href="/scam-education"
            className="rounded-lg border border-border px-8 py-3 text-sm font-semibold text-foreground hover:bg-muted transition-colors"
          >
            Learn About Scams
          </Link>
        </div>
        <p className="text-xs text-muted-foreground">No account required to scan. Free to use.</p>
      </section>

      {/* Trust bar */}
      <section className="border-y border-border bg-muted/30 py-6">
        <div className="mx-auto max-w-6xl px-4">
          <p className="text-center text-xs font-medium text-muted-foreground uppercase tracking-wider mb-4">
            Intelligence grounded in
          </p>
          <div className="flex flex-wrap justify-center gap-x-8 gap-y-3 text-sm font-medium text-muted-foreground">
            {["BSP Advisories", "SEC Philippines", "DICT Alerts", "PNP Cybercrime", "DMW Warnings"].map(
              (s) => (
                <span key={s} className="flex items-center gap-1.5">
                  <CheckCircle className="h-3.5 w-3.5 text-primary" aria-hidden />
                  {s}
                </span>
              )
            )}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-4 py-16 space-y-10">
        <div className="text-center space-y-3">
          <h2 className="text-2xl sm:text-3xl font-bold text-foreground">
            Four ways to catch a scam
          </h2>
          <p className="text-muted-foreground max-w-xl mx-auto">
            Every scam leaves traces. Our AI knows where to look.
          </p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {FEATURES.map(({ icon: Icon, title, description }) => (
            <div
              key={title}
              className="rounded-xl border border-border bg-card p-5 space-y-3 hover:shadow-sm transition-shadow"
            >
              <div className="inline-flex rounded-lg bg-primary/10 p-2.5">
                <Icon className="h-5 w-5 text-primary" aria-hidden />
              </div>
              <h3 className="font-semibold text-foreground">{title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="border-t border-border bg-muted/20 py-16">
        <div className="mx-auto max-w-4xl px-4 space-y-10">
          <div className="text-center space-y-3">
            <h2 className="text-2xl sm:text-3xl font-bold text-foreground">How it works</h2>
            <p className="text-muted-foreground">From submission to verdict in under 10 seconds.</p>
          </div>
          <div className="grid sm:grid-cols-3 gap-8">
            {HOW_IT_WORKS.map(({ step, title, description }) => (
              <div key={step} className="text-center space-y-3">
                <div className="mx-auto h-10 w-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold text-sm">
                  {step}
                </div>
                <h3 className="font-semibold text-foreground">{title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Scam types */}
      <section className="mx-auto max-w-6xl px-4 py-16 space-y-8">
        <div className="text-center space-y-3">
          <div className="inline-flex items-center gap-2 rounded-full bg-destructive/10 px-4 py-1.5 text-sm font-medium text-destructive">
            <AlertTriangle className="h-4 w-4" aria-hidden />
            Common in the Philippines
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-foreground">
            We detect these and more
          </h2>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 max-w-2xl mx-auto">
          {SCAM_TYPES.map((type) => (
            <div
              key={type}
              className="flex items-center gap-2 rounded-lg border border-border bg-card px-4 py-3 text-sm text-foreground"
            >
              <CheckCircle className="h-4 w-4 text-primary flex-shrink-0" aria-hidden />
              {type}
            </div>
          ))}
        </div>
        <div className="text-center pt-2">
          <Link
            href="/scam-education"
            className="inline-flex items-center gap-1.5 text-sm font-medium text-primary hover:underline"
          >
            <BookOpen className="h-4 w-4" aria-hidden />
            Read our Scam Education guide
          </Link>
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-border bg-primary py-16">
        <div className="mx-auto max-w-2xl px-4 text-center space-y-5">
          <h2 className="text-2xl sm:text-3xl font-bold text-primary-foreground">
            Received something suspicious?
          </h2>
          <p className="text-primary-foreground/80 leading-relaxed">
            Don&apos;t guess. Scan it now — no account required.
          </p>
          <Link
            href="/scanner"
            className="inline-block rounded-lg bg-background px-8 py-3 text-sm font-semibold text-foreground hover:bg-background/90 transition-colors"
          >
            Scan for Free
          </Link>
        </div>
      </section>
    </main>
  );
}
