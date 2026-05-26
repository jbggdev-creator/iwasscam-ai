"use client";

import { useState } from "react";
import { Loader2, Search } from "lucide-react";
import { urlScanSchema } from "@/lib/validations/scan";
import { scanUrl } from "@/lib/scan";
import { ScanResult } from "./ScanResult";
import type { ScanResult as ScanResultType } from "@/types/scan";

export function UrlScanForm() {
  const [url, setUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ScanResultType | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setResult(null);

    const parsed = urlScanSchema.safeParse({ url });
    if (!parsed.success) {
      setError(parsed.error.issues[0]?.message ?? "Invalid URL");
      return;
    }

    setIsLoading(true);
    try {
      const scanResult = await scanUrl(parsed.data.url);
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
        <label htmlFor="url-input" className="block text-sm font-medium text-foreground">
          Paste a suspicious URL
        </label>

        <div className="flex gap-2">
          <input
            id="url-input"
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://suspicious-site.example.com"
            disabled={isLoading}
            aria-describedby={error ? "url-error" : undefined}
            className="flex-1 rounded-lg border border-input bg-background px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !url.trim()}
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
            ) : (
              <Search className="h-4 w-4" aria-hidden />
            )}
            {isLoading ? "Scanning…" : "Scan"}
          </button>
        </div>

        {error && (
          <p id="url-error" role="alert" className="text-sm text-destructive">
            {error}
          </p>
        )}
      </form>

      {result && <ScanResult result={result} />}
    </div>
  );
}
