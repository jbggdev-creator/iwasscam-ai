import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { FindingsList } from "@/components/scanner/FindingsList";
import type { Finding } from "@/types/scan";

const FINDINGS: Finding[] = [
  {
    id: "f1",
    findingType: "very_new_domain",
    description: "Domain registered 2 days ago.",
    severity: "critical",
  },
  {
    id: "f2",
    findingType: "suspicious_tld",
    description: "Uses a .tk TLD commonly associated with phishing.",
    severity: "high",
  },
];

describe("FindingsList", () => {
  it("shows 'No suspicious indicators' when findings list is empty", () => {
    render(<FindingsList findings={[]} />);
    expect(screen.getByText("No suspicious indicators detected.")).toBeInTheDocument();
  });

  it("renders all findings", () => {
    render(<FindingsList findings={FINDINGS} />);
    expect(screen.getByText("Very New Domain")).toBeInTheDocument();
    expect(screen.getByText("Suspicious Domain Extension")).toBeInTheDocument();
  });

  it("renders finding descriptions", () => {
    render(<FindingsList findings={FINDINGS} />);
    expect(screen.getByText("Domain registered 2 days ago.")).toBeInTheDocument();
    expect(
      screen.getByText("Uses a .tk TLD commonly associated with phishing.")
    ).toBeInTheDocument();
  });

  it("falls back to raw findingType when label is not in FINDING_TYPE_LABELS", () => {
    const unknownFinding: Finding = {
      id: "f3",
      findingType: "custom_unknown_type",
      description: "Some custom finding.",
      severity: "medium",
    };
    render(<FindingsList findings={[unknownFinding]} />);
    expect(screen.getByText("custom_unknown_type")).toBeInTheDocument();
  });

  it("renders a single finding without showing others", () => {
    render(<FindingsList findings={[FINDINGS[0]]} />);
    expect(screen.getByText("Very New Domain")).toBeInTheDocument();
    expect(screen.queryByText("Suspicious Domain Extension")).not.toBeInTheDocument();
  });
});
