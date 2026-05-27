"use client";

import { useEffect, useState } from "react";
import { History, ChevronLeft, ChevronRight, Lock } from "lucide-react";
import Link from "next/link";
import { listScans } from "@/lib/scan";
import { ScanCard } from "@/components/scanner/ScanCard";
import { useSession } from "@/lib/auth";
import type { ScanResult } from "@/types/scan";

function LockedState({ label }: { label: string }) {
  return (
    <div className="relative">
      {/* blurred fake rows */}
      <div className="space-y-3 blur-sm pointer-events-none select-none" aria-hidden>
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-24 rounded-xl border border-border bg-muted/40" />
        ))}
      </div>
      {/* lock overlay */}
      <div className="absolute inset-0 flex flex-col items-center justify-center gap-4">
        <div className="flex flex-col items-center gap-3 rounded-2xl border border-border bg-background/90 px-8 py-7 shadow-lg backdrop-blur-sm text-center">
          <Lock className="h-8 w-8 text-primary" aria-hidden />
          <p className="text-sm font-semibold text-foreground">{label}</p>
          <p className="text-xs text-muted-foreground max-w-[220px]">
            Create a free account to save and revisit your scan results.
          </p>
          <div className="flex gap-2 pt-1">
            <Link
              href="/login"
              className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-foreground hover:bg-muted transition-colors"
            >
              Sign in
            </Link>
            <Link
              href="/register"
              className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90 transition-opacity"
            >
              Create account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function HistoryPage() {
  const { data: session, isPending } = useSession();
  const [scans, setScans] = useState<ScanResult[]>([]);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(false);

  const LIMIT = 20;

  useEffect(() => {
    if (!session) return;

    let cancelled = false;
    setIsLoading(true);
    setError(null);

    async function load() {
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
  }, [page, session]);

  return (
    <main className="mx-auto max-w-2xl px-4 py-8 space-y-6">
      <header className="space-y-1.5">
        <div className="flex items-center gap-2.5">
          <History className="h-6 w-6 text-primary flex-shrink-0" aria-hidden />
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Scan History</h1>
        </div>
        <p className="text-sm text-muted-foreground">
          Your personal scan history. Sign in to track and revisit results.
        </p>
      </header>

      {isPending && (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-24 rounded-xl border border-border bg-muted/40 animate-pulse" />
          ))}
        </div>
      )}

      {!isPending && !session && (
        <LockedState label="Sign in to view your scan history" />
      )}

      {!isPending && session && isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-24 rounded-xl border border-border bg-muted/40 animate-pulse" />
          ))}
        </div>
      )}

      {!isPending && session && error && (
        <div className="rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3">
          <p className="text-sm text-destructive">{error}</p>
        </div>
      )}

      {!isPending && session && !isLoading && !error && scans.length === 0 && (
        <div className="rounded-xl border border-border bg-muted/20 px-6 py-12 text-center">
          <History className="mx-auto h-10 w-10 text-muted-foreground mb-3" aria-hidden />
          <p className="text-sm font-medium text-foreground mb-1">No scans yet</p>
          <p className="text-sm text-muted-foreground">Run your first scan to see results here.</p>
        </div>
      )}

      {!isPending && session && !isLoading && scans.length > 0 && (
        <div className="space-y-3">
          {scans.map((scan) => (
            <ScanCard key={scan.id} scan={scan} />
          ))}
        </div>
      )}

      {!isPending && session && !isLoading && (page > 1 || hasMore) && (
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
