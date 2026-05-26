"use client";

import { useState } from "react";
import { Loader2, Phone } from "lucide-react";
import { phoneScanSchema } from "@/lib/validations/scan";
import { scanText } from "@/lib/scan";
import { ScanResult } from "./ScanResult";
import type { ScanResult as ScanResultType } from "@/types/scan";

export function PhoneScanForm() {
  const [phone, setPhone] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ScanResultType | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setResult(null);

    const parsed = phoneScanSchema.safeParse({ phone });
    if (!parsed.success) {
      setError(parsed.error.issues[0]?.message ?? "Invalid phone number");
      return;
    }

    setIsLoading(true);
    try {
      const scenario =
        `I received a suspicious call or SMS from this phone number: ${parsed.data.phone}. ` +
        `Is this a known scam number in the Philippines? Is it associated with fraud, spam, or scam activity?`;
      const scanResult = await scanText(scenario);
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
        <label htmlFor="phone-input" className="block text-sm font-medium text-foreground">
          Enter the phone or caller number
        </label>

        <div className="flex gap-2">
          <div className="relative flex-1">
            <span
              className="absolute left-3 top-1/2 -translate-y-1/2 text-base pointer-events-none select-none"
              aria-hidden
            >
              🇵🇭
            </span>
            <input
              id="phone-input"
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+63 917 123 4567"
              disabled={isLoading}
              aria-describedby={error ? "phone-error" : "phone-hint"}
              className="w-full rounded-lg border border-input bg-background pl-9 pr-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
            />
          </div>
          <button
            type="submit"
            disabled={isLoading || !phone.trim()}
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
            ) : (
              <Phone className="h-4 w-4" aria-hidden />
            )}
            {isLoading ? "Checking…" : "Check Number"}
          </button>
        </div>

        <p id="phone-hint" className="text-xs text-muted-foreground">
          Include the country code, e.g. +63 917 123 4567 or 09171234567
        </p>

        {error && (
          <p id="phone-error" role="alert" className="text-sm text-destructive">
            {error}
          </p>
        )}
      </form>

      {result && <ScanResult result={result} />}
    </div>
  );
}
