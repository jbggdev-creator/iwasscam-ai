export default function LandingPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="max-w-2xl text-center space-y-6">
        <h1 className="text-4xl font-bold tracking-tight text-foreground">
          IwasScam AI
        </h1>
        <p className="text-lg text-muted-foreground">
          AI-powered scam detection and trust verification for Filipinos.
          Upload screenshots, paste suspicious URLs, or describe a scenario —
          we&apos;ll analyze it for you.
        </p>
        <div className="flex gap-4 justify-center">
          <a
            href="/scanner"
            className="rounded-lg bg-primary px-6 py-3 text-primary-foreground font-semibold hover:opacity-90 transition-opacity"
          >
            Start Scanning
          </a>
          <a
            href="/login"
            className="rounded-lg border border-border px-6 py-3 text-foreground font-semibold hover:bg-muted transition-colors"
          >
            Sign In
          </a>
        </div>
      </div>
    </main>
  );
}
