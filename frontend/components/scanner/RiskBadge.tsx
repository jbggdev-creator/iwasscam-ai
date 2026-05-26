import { cva } from "class-variance-authority";
import { cn } from "@/lib/utils";
import type { RiskLevel } from "@/types/scan";

const badge = cva(
  "inline-flex items-center rounded-full px-3 py-1 text-sm font-semibold uppercase tracking-wide",
  {
    variants: {
      risk: {
        low: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
        medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
        high: "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400",
        critical: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
      },
    },
  }
);

const LABELS: Record<RiskLevel, string> = {
  low: "Low Risk",
  medium: "Medium Risk",
  high: "High Risk",
  critical: "Critical Risk",
};

interface RiskBadgeProps {
  risk: RiskLevel;
  className?: string;
}

export function RiskBadge({ risk, className }: RiskBadgeProps) {
  return (
    <span className={cn(badge({ risk }), className)}>
      {LABELS[risk]}
    </span>
  );
}
