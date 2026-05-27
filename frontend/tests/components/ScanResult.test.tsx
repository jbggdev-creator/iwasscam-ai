import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ScanResult } from "@/components/scanner/ScanResult";
import type { ScanResult as ScanResultType } from "@/types/scan";

const BASE_RESULT: ScanResultType = {
  id: "scan-abc",
  inputType: "url",
  riskLevel: "high",
  confidenceScore: 0.92,
  explanation: "This URL uses a newly registered domain with a suspicious TLD.",
  findings: [
    {
      id: "f1",
      findingType: "very_new_domain",
      description: "Domain registered 2 days ago.",
      severity: "critical",
    },
  ],
  createdAt: "2026-05-26T10:00:00.000Z",
};

describe("ScanResult", () => {
  it("renders the risk badge", () => {
    render(<ScanResult result={BASE_RESULT} />);
    expect(screen.getByText("High Risk")).toBeInTheDocument();
  });

  it("renders the confidence percentage", () => {
    render(<ScanResult result={BASE_RESULT} />);
    expect(screen.getByText("92%")).toBeInTheDocument();
  });

  it("renders the explanation text", () => {
    render(<ScanResult result={BASE_RESULT} />);
    expect(
      screen.getByText("This URL uses a newly registered domain with a suspicious TLD.")
    ).toBeInTheDocument();
  });

  it("renders the findings count header", () => {
    render(<ScanResult result={BASE_RESULT} />);
    expect(screen.getByText("Warning Signs (1)")).toBeInTheDocument();
  });

  it("renders the finding description", () => {
    render(<ScanResult result={BASE_RESULT} />);
    expect(screen.getByText("Domain registered 2 days ago.")).toBeInTheDocument();
  });

  it("does not render findings section when there are no findings", () => {
    const noFindings: ScanResultType = { ...BASE_RESULT, findings: [] };
    render(<ScanResult result={noFindings} />);
    expect(screen.queryByText(/Warning Signs/)).not.toBeInTheDocument();
  });

  it("renders confidence as 0% when score is 0", () => {
    const zeroConf: ScanResultType = { ...BASE_RESULT, confidenceScore: 0 };
    render(<ScanResult result={zeroConf} />);
    expect(screen.getByText("0%")).toBeInTheDocument();
  });

  it("rounds confidence to nearest integer", () => {
    const result: ScanResultType = { ...BASE_RESULT, confidenceScore: 0.756 };
    render(<ScanResult result={result} />);
    expect(screen.getByText("76%")).toBeInTheDocument();
  });
});
