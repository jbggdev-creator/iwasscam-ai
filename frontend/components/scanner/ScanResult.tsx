import { Shield } from "lucide-react";
import { RiskBadge } from "./RiskBadge";
import { FindingsList } from "./FindingsList";
import type { ScanResult } from "@/types/scan";

interface ScanResultProps {
  result: ScanResult;
}

export function ScanResult({ result }: ScanResultProps) {
  const confidencePct = Math.round(result.confidenceScore * 100);

  return (
    <div className="rounded-xl border border-border bg-card p-6 space-y-5 shadow-sm">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-3">
          <Shield className="h-6 w-6 text-muted-foreground flex-shrink-0" aria-hidden />
          <div>
            <p className="text-xs text-muted-foreground uppercase tracking-wide font-medium mb-1">
              Scan Result
            </p>
            <RiskBadge risk={result.riskLevel} />
          </div>
        </div>
        <div className="text-right">
          <p className="text-xs text-muted-foreground uppercase tracking-wide font-medium mb-1">
            Confidence
          </p>
          <p className="text-2xl font-bold text-foreground">{confidencePct}%</p>
        </div>
      </div>

      {/* Explanation */}
      <div>
        <p className="text-sm font-medium text-foreground mb-1">Analysis</p>
        <p className="text-sm text-muted-foreground leading-relaxed">{result.explanation}</p>
      </div>

      {/* Findings */}
      {result.findings.length > 0 && (
        <div>
          <p className="text-sm font-medium text-foreground mb-3">
            Warning Signs ({result.findings.length})
          </p>
          <FindingsList findings={result.findings} />
        </div>
      )}

      <p className="text-xs text-muted-foreground pt-1 border-t border-border">
        Scanned at {new Date(result.createdAt).toLocaleString("en-PH")}
      </p>
    </div>
  );
}
