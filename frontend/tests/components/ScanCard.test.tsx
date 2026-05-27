import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { ScanCard } from "@/components/scanner/ScanCard";
import type { ScanResult } from "@/types/scan";

vi.mock("next/link", () => ({
  default: ({ href, children, ...props }: { href: string; children: React.ReactNode }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

const BASE_SCAN: ScanResult = {
  id: "scan-card-1",
  inputType: "url",
  riskLevel: "high",
  confidenceScore: 0.85,
  explanation: "This URL is likely a phishing attempt.",
  findings: [
    { id: "f1", findingType: "very_new_domain", description: "2 days old.", severity: "critical" },
    { id: "f2", findingType: "suspicious_tld", description: "Suspicious TLD.", severity: "high" },
  ],
  createdAt: "2026-05-26T10:00:00Z",
};

describe("ScanCard", () => {
  it("renders a link to the scan detail page", () => {
    render(<ScanCard scan={BASE_SCAN} />);
    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", "/history/scan-card-1");
  });

  it("renders the risk badge", () => {
    render(<ScanCard scan={BASE_SCAN} />);
    expect(screen.getByText("High Risk")).toBeInTheDocument();
  });

  it("renders the explanation text", () => {
    render(<ScanCard scan={BASE_SCAN} />);
    expect(screen.getByText("This URL is likely a phishing attempt.")).toBeInTheDocument();
  });

  it("renders the input type label", () => {
    render(<ScanCard scan={BASE_SCAN} />);
    expect(screen.getByText("URL")).toBeInTheDocument();
  });

  it("renders the findings count", () => {
    render(<ScanCard scan={BASE_SCAN} />);
    expect(screen.getByText(/2 warnings/)).toBeInTheDocument();
  });

  it("renders singular 'warning' for one finding", () => {
    const oneFinding: ScanResult = { ...BASE_SCAN, findings: [BASE_SCAN.findings[0]] };
    render(<ScanCard scan={oneFinding} />);
    expect(screen.getByText(/1 warning$/)).toBeInTheDocument();
  });

  it("does not render findings count when findings is empty", () => {
    const noFindings: ScanResult = { ...BASE_SCAN, findings: [] };
    render(<ScanCard scan={noFindings} />);
    expect(screen.queryByText(/warning/)).not.toBeInTheDocument();
  });

  it("renders confidence percentage", () => {
    render(<ScanCard scan={BASE_SCAN} />);
    expect(screen.getByText("85% confidence")).toBeInTheDocument();
  });

  it("renders correct label for 'text' input type", () => {
    const textScan: ScanResult = { ...BASE_SCAN, inputType: "text" };
    render(<ScanCard scan={textScan} />);
    expect(screen.getByText("Scenario")).toBeInTheDocument();
  });

  it("renders correct label for 'image' input type", () => {
    const imageScan: ScanResult = { ...BASE_SCAN, inputType: "image" };
    render(<ScanCard scan={imageScan} />);
    expect(screen.getByText("Screenshot")).toBeInTheDocument();
  });
});
