import Link from "next/link";
import { RiskBadge } from "./RiskBadge";
import type { ScanResult } from "@/types/scan";

const INPUT_TYPE_LABELS: Record<ScanResult["inputType"], string> = {
  url: "URL",
  image: "Screenshot",
  text: "Scenario",
  qr: "QR Code",
};

interface ScanCardProps {
  scan: ScanResult;
}

export function ScanCard({ scan }: ScanCardProps) {
  return (
    <Link
      href={`/history/${scan.id}`}
      className="block rounded-xl border border-border bg-card p-4 hover:bg-muted/50 transition-colors"
    >
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div className="space-y-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              {INPUT_TYPE_LABELS[scan.inputType]}
            </span>
            {scan.findings.length > 0 && (
              <span className="text-xs text-muted-foreground">
                · {scan.findings.length} warning{scan.findings.length !== 1 ? "s" : ""}
              </span>
            )}
          </div>
          <p className="text-sm text-foreground line-clamp-2 leading-relaxed">
            {scan.explanation}
          </p>
        </div>
        <div className="flex flex-col items-end gap-1.5 shrink-0">
          <RiskBadge risk={scan.riskLevel} />
          <span className="text-xs text-muted-foreground">
            {Math.round(scan.confidenceScore * 100)}% confidence
          </span>
        </div>
      </div>
      <p className="mt-3 text-xs text-muted-foreground border-t border-border pt-2">
        {new Date(scan.createdAt).toLocaleString("en-PH")}
      </p>
    </Link>
  );
}
