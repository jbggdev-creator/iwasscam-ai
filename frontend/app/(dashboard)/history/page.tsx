"use client";

import { useEffect, useState } from "react";
import { History, ChevronLeft, ChevronRight } from "lucide-react";
import { listScans } from "@/lib/scan";
import { ScanCard } from "@/components/scanner/ScanCard";
import type { ScanResult } from "@/types/scan";

export default function HistoryPage() {
  const [scans, setScans] = useState<ScanResult[]>([]);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(false);

  const LIMIT = 20;

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setIsLoading(true);
      setError(null);
      try {
        const result = await listScans(page, LIMIT);
        if (!cancelled) {
          setScans(result.scans);
          setHasMore(result.scans.length === LIMIT);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load history");
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    load();
    return () => { cancelled = true; };
  }, [page]);

  return (
    <main className="mx-auto max-w-2xl px-4 py-8 space-y-6">
      <header className="space-y-1.5">
        <div className="flex items-center gap-2.5">
          <History className="h-6 w-6 text-primary flex-shrink-0" aria-hidden />
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Scan History</h1>
        </div>
        <p className="text-sm text-muted-foreground">
          Recent scans across all users. Sign in to track your own scans.
        </p>
      </header>

      {isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div
              key={i}
              className="h-24 rounded-xl border border-border bg-muted/40 animate-pulse"
            />
          ))}
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3">
          <p className="text-sm text-destructive">{error}</p>
        </div>
      )}

      {!isLoading && !error && scans.length === 0 && (
        <div className="rounded-xl border border-border bg-muted/20 px-6 py-12 text-center">
          <History className="mx-auto h-10 w-10 text-muted-foreground mb-3" aria-hidden />
          <p className="text-sm font-medium text-foreground mb-1">No scans yet</p>
          <p className="text-sm text-muted-foreground">
            Run your first scan to see results here.
          </p>
        </div>
      )}

      {!isLoading && scans.length > 0 && (
        <div className="space-y-3">
          {scans.map((scan) => (
            <ScanCard key={scan.id} scan={scan} />
          ))}
        </div>
      )}

      {!isLoading && (page > 1 || hasMore) && (
        <div className="flex items-center justify-between pt-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="h-4 w-4" aria-hidden />
            Previous
          </button>
          <span className="text-sm text-muted-foreground">Page {page}</span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={!hasMore}
            className="inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Next
            <ChevronRight className="h-4 w-4" aria-hidden />
          </button>
        </div>
      )}
    </main>
  );
}
