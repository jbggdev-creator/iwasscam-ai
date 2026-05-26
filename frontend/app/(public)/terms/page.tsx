import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms of Service — IwasScam AI",
  description: "Terms of service for using the IwasScam AI platform.",
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

export default function TermsPage() {
  return (
    <main className="mx-auto max-w-3xl px-4 py-12">
      <header className="mb-10 space-y-2">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Terms of Service</h1>
        <p className="text-sm text-muted-foreground">Last updated: {LAST_UPDATED}</p>
      </header>

      <div className="space-y-8">
        <Section title="1. Acceptance">
          <p className="text-muted-foreground leading-relaxed">
            By accessing or using IwasScam AI (&quot;the Service&quot;), you agree to be bound by
            these Terms. If you do not agree, do not use the Service.
          </p>
        </Section>

        <Section title="2. Description of service">
          <p className="text-muted-foreground leading-relaxed">
            IwasScam AI provides AI-powered scam detection and risk scoring for URLs, images,
            QR codes, and text scenarios. The Service is intended to assist users in identifying
            potentially fraudulent content — it does not constitute legal advice, financial
            advice, or a definitive determination of criminal activity.
          </p>
        </Section>

        <Section title="3. No guarantee of accuracy">
          <p className="text-muted-foreground leading-relaxed">
            Risk scores and findings are probabilistic estimates based on available signals.
            The Service may produce false positives or false negatives. Do not rely solely on
            IwasScam AI to make financial or security decisions. Always apply independent judgment
            and consult official Philippine government agencies when in doubt.
          </p>
        </Section>

        <Section title="4. Acceptable use">
          <p className="text-muted-foreground leading-relaxed mb-2">You agree not to:</p>
          <ul className="space-y-2 text-muted-foreground list-none">
            <li>— Submit content that violates Philippine law or the rights of others</li>
            <li>— Attempt to reverse-engineer, scrape, or abuse the Service at scale</li>
            <li>— Use the Service to harass, defame, or falsely accuse individuals</li>
            <li>— Circumvent rate limits or attempt to disrupt service availability</li>
            <li>— Submit malware, exploits, or malicious payloads via the upload feature</li>
          </ul>
        </Section>

        <Section title="5. User content">
          <p className="text-muted-foreground leading-relaxed">
            You retain ownership of any content you submit. By submitting content, you grant us
            a limited license to process it solely for the purpose of providing the Service.
            We do not claim ownership of your submissions.
          </p>
        </Section>

        <Section title="6. Limitation of liability">
          <p className="text-muted-foreground leading-relaxed">
            To the maximum extent permitted by applicable law, IwasScam AI and its operators
            shall not be liable for any indirect, incidental, or consequential damages arising
            from your use of the Service, including financial losses resulting from acting on a
            risk assessment provided by the platform.
          </p>
        </Section>

        <Section title="7. Disclaimers">
          <p className="text-muted-foreground leading-relaxed">
            The Service is provided &quot;as is&quot; without warranties of any kind, express or implied.
            We do not warrant that the Service will be uninterrupted, error-free, or that it will
            detect all scams. Risk assessments are informational only.
          </p>
        </Section>

        <Section title="8. Account termination">
          <p className="text-muted-foreground leading-relaxed">
            We reserve the right to suspend or terminate accounts that violate these Terms or
            pose a security risk. You may delete your account at any time from the Settings page.
          </p>
        </Section>

        <Section title="9. Governing law">
          <p className="text-muted-foreground leading-relaxed">
            These Terms are governed by the laws of the Republic of the Philippines. Disputes
            shall be resolved in the appropriate courts of the Philippines.
          </p>
        </Section>

        <Section title="10. Changes to these terms">
          <p className="text-muted-foreground leading-relaxed">
            We may update these Terms periodically. Continued use of the Service after changes
            are posted constitutes acceptance of the revised Terms.
          </p>
        </Section>

        <Section title="11. Contact">
          <p className="text-muted-foreground leading-relaxed">
            Questions about these Terms? Email{" "}
            <a href="mailto:legal@iwasscam.ai" className="text-primary hover:underline">
              legal@iwasscam.ai
            </a>
            .
          </p>
        </Section>
      </div>
    </main>
  );
}
