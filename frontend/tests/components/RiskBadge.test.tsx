import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { RiskBadge } from "@/components/scanner/RiskBadge";

describe("RiskBadge", () => {
  it("renders 'Low Risk' for low", () => {
    render(<RiskBadge risk="low" />);
    expect(screen.getByText("Low Risk")).toBeInTheDocument();
  });

  it("renders 'Medium Risk' for medium", () => {
    render(<RiskBadge risk="medium" />);
    expect(screen.getByText("Medium Risk")).toBeInTheDocument();
  });

  it("renders 'High Risk' for high", () => {
    render(<RiskBadge risk="high" />);
    expect(screen.getByText("High Risk")).toBeInTheDocument();
  });

  it("renders 'Critical Risk' for critical", () => {
    render(<RiskBadge risk="critical" />);
    expect(screen.getByText("Critical Risk")).toBeInTheDocument();
  });

  it("applies green styling for low risk", () => {
    render(<RiskBadge risk="low" />);
    const badge = screen.getByText("Low Risk");
    expect(badge.className).toContain("green");
  });

  it("applies red styling for critical risk", () => {
    render(<RiskBadge risk="critical" />);
    const badge = screen.getByText("Critical Risk");
    expect(badge.className).toContain("red");
  });
});
