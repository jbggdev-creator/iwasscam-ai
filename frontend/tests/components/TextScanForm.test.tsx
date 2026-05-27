import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TextScanForm } from "@/components/scanner/TextScanForm";
import type { ScanResult } from "@/types/scan";

vi.mock("@/lib/scan", () => ({
  scanText: vi.fn(),
}));

import { scanText } from "@/lib/scan";

const MOCK_RESULT: ScanResult = {
  id: "scan-text-1",
  inputType: "text",
  riskLevel: "critical",
  confidenceScore: 0.95,
  explanation: "Classic job scam pattern detected.",
  findings: [],
  createdAt: "2026-05-26T10:00:00Z",
};

describe("TextScanForm", () => {
  beforeEach(() => {
    vi.mocked(scanText).mockReset();
  });

  it("renders the textarea and Analyze button", () => {
    render(<TextScanForm />);
    expect(screen.getByLabelText("Describe what happened")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /analyze scenario/i })).toBeInTheDocument();
  });

  it("Analyze button is disabled when input is empty", () => {
    render(<TextScanForm />);
    expect(screen.getByRole("button", { name: /analyze scenario/i })).toBeDisabled();
  });

  it("Analyze button is disabled when input is fewer than 10 characters", async () => {
    render(<TextScanForm />);
    await userEvent.type(screen.getByLabelText("Describe what happened"), "too short");
    expect(screen.getByRole("button", { name: /analyze scenario/i })).toBeDisabled();
  });

  it("Analyze button is enabled when input has 10+ characters", async () => {
    render(<TextScanForm />);
    await userEvent.type(screen.getByLabelText("Describe what happened"), "exactly 10");
    expect(screen.getByRole("button", { name: /analyze scenario/i })).not.toBeDisabled();
  });

  it("shows character countdown", async () => {
    render(<TextScanForm />);
    const textarea = screen.getByLabelText("Describe what happened");
    await userEvent.type(textarea, "hello");
    expect(screen.getByText("1995")).toBeInTheDocument();
  });

  it("does not call scanText when button is disabled", async () => {
    render(<TextScanForm />);
    const textarea = screen.getByLabelText("Describe what happened");
    await userEvent.type(textarea, "too short");

    expect(screen.getByRole("button", { name: /analyze scenario/i })).toBeDisabled();
    expect(scanText).not.toHaveBeenCalled();
  });

  it("calls scanText with the scenario on valid submit", async () => {
    vi.mocked(scanText).mockResolvedValueOnce(MOCK_RESULT);
    render(<TextScanForm />);

    const scenario = "A recruiter asked me to pay ₱500 before my first day at work.";
    await userEvent.type(screen.getByLabelText("Describe what happened"), scenario);
    await userEvent.click(screen.getByRole("button", { name: /analyze scenario/i }));

    expect(scanText).toHaveBeenCalledWith(scenario);
  });

  it("displays scan result after successful analysis", async () => {
    vi.mocked(scanText).mockResolvedValueOnce(MOCK_RESULT);
    render(<TextScanForm />);

    await userEvent.type(
      screen.getByLabelText("Describe what happened"),
      "A recruiter asked me to pay ₱500 before my first day."
    );
    await userEvent.click(screen.getByRole("button", { name: /analyze scenario/i }));

    expect(await screen.findByText("Critical Risk")).toBeInTheDocument();
    expect(screen.getByText("Classic job scam pattern detected.")).toBeInTheDocument();
  });

  it("shows error message when scanText throws", async () => {
    vi.mocked(scanText).mockRejectedValueOnce(new Error("Analysis failed"));
    render(<TextScanForm />);

    await userEvent.type(
      screen.getByLabelText("Describe what happened"),
      "A recruiter asked me to pay ₱500 before my first day."
    );
    await userEvent.click(screen.getByRole("button", { name: /analyze scenario/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Analysis failed");
  });
});
