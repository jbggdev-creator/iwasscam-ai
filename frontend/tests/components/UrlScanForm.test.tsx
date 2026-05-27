import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { UrlScanForm } from "@/components/scanner/UrlScanForm";
import type { ScanResult } from "@/types/scan";

vi.mock("@/lib/scan", () => ({
  scanUrl: vi.fn(),
}));

import { scanUrl } from "@/lib/scan";

const MOCK_RESULT: ScanResult = {
  id: "scan-1",
  inputType: "url",
  riskLevel: "high",
  confidenceScore: 0.9,
  explanation: "Suspicious domain detected.",
  findings: [],
  createdAt: "2026-05-26T10:00:00Z",
};

describe("UrlScanForm", () => {
  beforeEach(() => {
    vi.mocked(scanUrl).mockReset();
  });

  it("renders the URL input and Scan button", () => {
    render(<UrlScanForm />);
    expect(screen.getByLabelText("Paste a suspicious URL")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /scan/i })).toBeInTheDocument();
  });

  it("Scan button is disabled when input is empty", () => {
    render(<UrlScanForm />);
    expect(screen.getByRole("button", { name: /scan/i })).toBeDisabled();
  });

  it("shows validation error for invalid URL on submit", async () => {
    render(<UrlScanForm />);
    const input = screen.getByLabelText("Paste a suspicious URL");
    await userEvent.type(input, "not-a-url");
    // fireEvent.submit bypasses native HTML URL constraint validation so Zod runs
    fireEvent.submit(input.closest("form")!);

    expect(await screen.findByRole("alert")).toHaveTextContent("Please enter a valid URL");
    expect(scanUrl).not.toHaveBeenCalled();
  });

  it("calls scanUrl with the entered URL on valid submit", async () => {
    vi.mocked(scanUrl).mockResolvedValueOnce(MOCK_RESULT);
    render(<UrlScanForm />);

    const input = screen.getByLabelText("Paste a suspicious URL");
    await userEvent.type(input, "https://suspicious-site.example.com");
    await userEvent.click(screen.getByRole("button", { name: /scan/i }));

    expect(scanUrl).toHaveBeenCalledWith("https://suspicious-site.example.com");
  });

  it("displays scan result after successful scan", async () => {
    vi.mocked(scanUrl).mockResolvedValueOnce(MOCK_RESULT);
    render(<UrlScanForm />);

    const input = screen.getByLabelText("Paste a suspicious URL");
    await userEvent.type(input, "https://suspicious-site.example.com");
    await userEvent.click(screen.getByRole("button", { name: /scan/i }));

    expect(await screen.findByText("High Risk")).toBeInTheDocument();
    expect(screen.getByText("Suspicious domain detected.")).toBeInTheDocument();
  });

  it("shows error message when scanUrl throws", async () => {
    vi.mocked(scanUrl).mockRejectedValueOnce(new Error("Rate limit exceeded"));
    render(<UrlScanForm />);

    const input = screen.getByLabelText("Paste a suspicious URL");
    await userEvent.type(input, "https://suspicious-site.example.com");
    await userEvent.click(screen.getByRole("button", { name: /scan/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Rate limit exceeded");
  });

  it("shows fallback error when a non-Error is thrown", async () => {
    vi.mocked(scanUrl).mockRejectedValueOnce("unexpected");
    render(<UrlScanForm />);

    await userEvent.type(
      screen.getByLabelText("Paste a suspicious URL"),
      "https://example.com"
    );
    await userEvent.click(screen.getByRole("button", { name: /scan/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Something went wrong");
  });
});
