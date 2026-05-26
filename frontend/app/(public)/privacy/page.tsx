import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy — IwasScam AI",
  description: "How IwasScam AI collects, uses, and protects your data.",
};

const LAST_UPDATED = "May 26, 2026";

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-3">
      <h2 className="text-base font-semibold text-foreground">{title}</h2>
      {children}
    </section>
  );
}

export default function PrivacyPage() {
  return (
    <main className="mx-auto max-w-3xl px-4 py-12">
      <header className="mb-10 space-y-2">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Privacy Policy</h1>
        <p className="text-sm text-muted-foreground">Last updated: {LAST_UPDATED}</p>
      </header>

      <div className="space-y-8">
        <Section title="1. Overview">
          <p className="text-muted-foreground leading-relaxed">
            IwasScam AI (&quot;we,&quot; &quot;our,&quot; or &quot;the platform&quot;) is committed to protecting your
            privacy. This policy explains what information we collect, how we use it, and the
            choices you have. We process data solely to provide scam detection services and
            improve platform safety.
          </p>
        </Section>

        <Section title="2. Information we collect">
          <ul className="space-y-3 text-muted-foreground list-none">
            <li>
              <strong className="text-foreground">Scan submissions.</strong> URLs, text scenarios,
              and image files you submit for analysis. Images are processed in memory and not
              permanently stored after analysis completes.
            </li>
            <li>
              <strong className="text-foreground">Account information.</strong> If you register:
              your name and email address. Passwords are hashed and never stored in plaintext.
            </li>
            <li>
              <strong className="text-foreground">Scan results.</strong> Risk scores, findings,
              and explanations are stored in your scan history.
            </li>
            <li>
              <strong className="text-foreground">Usage data.</strong> Request timestamps, IP
              addresses (for rate limiting), and HTTP request metadata. We do not build behavioral
              profiles.
            </li>
          </ul>
        </Section>

        <Section title="3. What we do NOT collect">
          <ul className="space-y-2 text-muted-foreground list-none">
            <li>— Uploaded images or screenshots after analysis completes</li>
            <li>— The content of your personal messages or conversations</li>
            <li>— Data shared with advertisers or third-party data brokers</li>
            <li>— Data used to train AI models without explicit consent</li>
          </ul>
        </Section>

        <Section title="4. How we use your information">
          <ul className="space-y-2 text-muted-foreground list-none">
            <li>— To perform scam analysis and return a risk verdict</li>
            <li>— To display your scan history in your dashboard</li>
            <li>— To enforce rate limits and protect the service from abuse</li>
            <li>— To aggregate anonymized threat intelligence to improve detection accuracy</li>
          </ul>
        </Section>

        <Section title="5. Data retention">
          <p className="text-muted-foreground leading-relaxed">
            Scan records (risk level, findings, explanation — no raw image data) are retained for
            90 days. Account data is retained while your account is active and deleted within 30
            days of account deletion. You may request deletion at any time by contacting us.
          </p>
        </Section>

        <Section title="6. Third-party services">
          <p className="text-muted-foreground leading-relaxed">
            We use third-party services for infrastructure (database hosting, error monitoring).
            These services process data only as necessary and are bound by data processing
            agreements. Analysis is performed on-premise — we do not share your content with
            external AI API providers.
          </p>
        </Section>

        <Section title="7. Security">
          <p className="text-muted-foreground leading-relaxed">
            We use HTTPS for all data in transit, encrypted database connections, and httpOnly
            cookies for session management. We follow OWASP security best practices and conduct
            periodic security reviews.
          </p>
        </Section>

        <Section title="8. Your rights">
          <p className="text-muted-foreground leading-relaxed">
            You have the right to access, correct, and delete your personal data. Contact us at
            the email below. We will respond within 15 business days.
          </p>
        </Section>

        <Section title="9. Changes to this policy">
          <p className="text-muted-foreground leading-relaxed">
            We may update this policy periodically. Material changes will be communicated via
            email (if you have an account) or via a notice on the platform. Continued use after
            notice constitutes acceptance.
          </p>
        </Section>

        <Section title="10. Contact">
          <p className="text-muted-foreground leading-relaxed">
            Questions about this policy? Email us at{" "}
            <a href="mailto:privacy@iwasscam.ai" className="text-primary hover:underline">
              privacy@iwasscam.ai
            </a>
            .
          </p>
        </Section>
      </div>
    </main>
  );
}
