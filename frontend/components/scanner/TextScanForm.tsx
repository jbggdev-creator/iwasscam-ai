"use client";

import { useState } from "react";
import { Loader2, Send } from "lucide-react";
import { textScanSchema } from "@/lib/validations/scan";
import { scanText } from "@/lib/scan";
import { ScanResult } from "./ScanResult";
import type { ScanResult as ScanResultType } from "@/types/scan";

export function TextScanForm() {
  const [scenario, setScenario] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ScanResultType | null>(null);
  const [error, setError] = useState<string | null>(null);

  const remaining = 2000 - scenario.length;

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setResult(null);

    const parsed = textScanSchema.safeParse({ scenario });
    if (!parsed.success) {
      setError(parsed.error.issues[0]?.message ?? "Invalid input");
      return;
    }

    setIsLoading(true);
    try {
      const scanResult = await scanText(parsed.data.scenario);
      setResult(scanResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="space-y-3">
        <label htmlFor="scenario-input" className="block text-sm font-medium text-foreground">
          Describe what happened
        </label>

        <div className="relative">
          <textarea
            id="scenario-input"
            value={scenario}
            onChange={(e) => setScenario(e.target.value)}
            placeholder={
              "e.g. A recruiter asked me to pay ₱500 for onboarding before my first day. " +
              "They said it's a refundable deposit. Is this a scam?"
            }
            rows={5}
            disabled={isLoading}
            aria-describedby={error ? "scenario-error" : "scenario-counter"}
            className="w-full rounded-lg border border-input bg-background px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50 resize-none leading-relaxed"
          />
          <span
            id="scenario-counter"
            aria-live="polite"
            className={`absolute bottom-2.5 right-3 text-xs tabular-nums pointer-events-none ${
              remaining < 100 ? "text-destructive" : "text-muted-foreground"
            }`}
          >
            {remaining}
          </span>
        </div>

        {error && (
          <p id="scenario-error" role="alert" className="text-sm text-destructive">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={isLoading || scenario.trim().length < 10}
          className="inline-flex w-full sm:w-auto items-center justify-center gap-2 rounded-lg bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
          ) : (
            <Send className="h-4 w-4" aria-hidden />
          )}
          {isLoading ? "Analyzing…" : "Analyze Scenario"}
        </button>
      </form>

      {result && <ScanResult result={result} />}
    </div>
  );
}
