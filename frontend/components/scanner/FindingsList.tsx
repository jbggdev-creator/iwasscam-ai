import { AlertTriangle, AlertCircle, Info, CheckCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Finding, RiskLevel } from "@/types/scan";

const SEVERITY_CONFIG: Record<
  RiskLevel,
  { icon: React.ElementType; color: string; label: string }
> = {
  low: { icon: Info, color: "text-green-600 dark:text-green-400", label: "Low" },
  medium: { icon: AlertCircle, color: "text-yellow-600 dark:text-yellow-400", label: "Medium" },
  high: { icon: AlertTriangle, color: "text-orange-600 dark:text-orange-400", label: "High" },
  critical: { icon: AlertTriangle, color: "text-red-600 dark:text-red-400", label: "Critical" },
};

const FINDING_TYPE_LABELS: Record<string, string> = {
  very_new_domain: "Very New Domain",
  new_domain: "New Domain",
  recent_domain: "Recent Domain",
  whois_unavailable: "WHOIS Unavailable",
  suspicious_tld: "Suspicious Domain Extension",
  invalid_ssl: "Invalid SSL Certificate",
  high_url_entropy: "Obfuscated URL",
  excessive_redirects: "Excessive Redirects",
};

interface FindingsListProps {
  findings: Finding[];
  className?: string;
}

export function FindingsList({ findings, className }: FindingsListProps) {
  if (findings.length === 0) {
    return (
      <div className={cn("flex items-center gap-2 text-green-600 dark:text-green-400", className)}>
        <CheckCircle className="h-4 w-4 flex-shrink-0" />
        <span className="text-sm">No suspicious indicators detected.</span>
      </div>
    );
  }

  return (
    <ul className={cn("space-y-3", className)}>
      {findings.map((finding) => {
        const config = SEVERITY_CONFIG[finding.severity] ?? SEVERITY_CONFIG.medium;
        const Icon = config.icon;
        const label = FINDING_TYPE_LABELS[finding.findingType] ?? finding.findingType;

        return (
          <li key={finding.id} className="flex gap-3">
            <Icon className={cn("h-5 w-5 flex-shrink-0 mt-0.5", config.color)} aria-hidden />
            <div className="min-w-0">
              <p className="text-sm font-medium text-foreground">{label}</p>
              <p className="text-sm text-muted-foreground">{finding.description}</p>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
