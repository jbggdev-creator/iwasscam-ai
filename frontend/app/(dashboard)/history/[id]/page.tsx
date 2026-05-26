"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Shield } from "lucide-react";
import { getScan } from "@/lib/scan";
import { ScanResult } from "@/components/scanner/ScanResult";
import type { ScanResult as ScanResultType } from "@/types/scan";

export default function ScanDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [scan, setScan] = useState<ScanResultType | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    let cancelled = false;

    async function load() {
      try {
        const result = await getScan(id);
        if (!cancelled) setScan(result);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Scan not found");
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    load();
    return () => { cancelled = true; };
  }, [id]);

  return (
    <main className="mx-auto max-w-2xl px-4 py-8 space-y-6">
      <div>
        <button
          onClick={() => router.back()}
          className="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
        >
          <ArrowLeft className="h-4 w-4" aria-hidden />
          Back
        </button>
      </div>

      <header className="flex items-center gap-2.5">
        <Shield className="h-6 w-6 text-primary flex-shrink-0" aria-hidden />
        <h1 className="text-2xl font-bold tracking-tight text-foreground">Scan Detail</h1>
      </header>

      {isLoading && (
        <div className="rounded-xl border border-border bg-muted/40 h-48 animate-pulse" />
      )}

      {error && (
        <div className="rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3">
          <p className="text-sm text-destructive">{error}</p>
        </div>
      )}

      {!isLoading && scan && <ScanResult result={scan} />}
    </main>
  );
}
