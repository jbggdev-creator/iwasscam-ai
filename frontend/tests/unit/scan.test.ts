import { describe, it, expect, vi, beforeEach } from "vitest";
import { scanUrl, scanText, scanImage, scanQr, getScan, listScans } from "@/lib/scan";

const RAW_SCAN = {
  id: "scan-123",
  input_type: "url",
  risk_level: "high",
  confidence_score: 0.87,
  explanation: "This domain was registered 2 days ago.",
  findings: [
    {
      id: "f1",
      finding_type: "very_new_domain",
      description: "Domain registered 2 days ago.",
      severity: "critical",
    },
  ],
  created_at: "2026-05-26T10:00:00Z",
};

function mockFetch(data: unknown, status = 200) {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValueOnce(new Response(JSON.stringify(data), { status }))
  );
}

describe("scanUrl", () => {
  beforeEach(() => vi.unstubAllGlobals());

  it("returns a ScanResult in camelCase on success", async () => {
    mockFetch(RAW_SCAN);
    const result = await scanUrl("https://scam.example.com");

    expect(result.id).toBe("scan-123");
    expect(result.inputType).toBe("url");
    expect(result.riskLevel).toBe("high");
    expect(result.confidenceScore).toBe(0.87);
    expect(result.findings[0].findingType).toBe("very_new_domain");
    expect(result.findings[0].severity).toBe("critical");
    expect(result.createdAt).toBe("2026-05-26T10:00:00Z");
  });

  it("throws with backend error message on failure", async () => {
    mockFetch({ detail: "Rate limit exceeded" }, 429);
    await expect(scanUrl("https://scam.example.com")).rejects.toThrow("Rate limit exceeded");
  });

  it("throws generic message when backend gives no detail", async () => {
    mockFetch({ message: "Server error" }, 500);
    await expect(scanUrl("https://scam.example.com")).rejects.toThrow("Server error");
  });
});

describe("scanText", () => {
  beforeEach(() => vi.unstubAllGlobals());

  it("returns a ScanResult on success", async () => {
    const rawText = { ...RAW_SCAN, input_type: "text" };
    mockFetch(rawText);

    const result = await scanText("Someone asked me to pay ₱500 upfront.");
    expect(result.inputType).toBe("text");
    expect(result.riskLevel).toBe("high");
  });

  it("throws on error", async () => {
    mockFetch({ detail: "Text scan failed" }, 500);
    await expect(scanText("some scenario")).rejects.toThrow("Text scan failed");
  });
});

describe("getScan", () => {
  beforeEach(() => vi.unstubAllGlobals());

  it("returns a ScanResult by ID", async () => {
    mockFetch(RAW_SCAN);
    const result = await getScan("scan-123");
    expect(result.id).toBe("scan-123");
  });

  it("throws when scan not found", async () => {
    mockFetch({ detail: "Scan not found" }, 404);
    await expect(getScan("nonexistent")).rejects.toThrow("Scan not found");
  });
});

describe("scanImage", () => {
  beforeEach(() => vi.unstubAllGlobals());

  it("returns a ScanResult on success", async () => {
    const rawImage = { ...RAW_SCAN, input_type: "image" };
    mockFetch(rawImage);

    const file = new File(["data"], "receipt.png", { type: "image/png" });
    const result = await scanImage(file);
    expect(result.inputType).toBe("image");
    expect(result.id).toBe("scan-123");
  });

  it("throws on error", async () => {
    mockFetch({ detail: "Image scan failed" }, 501);
    const file = new File(["data"], "receipt.png", { type: "image/png" });
    await expect(scanImage(file)).rejects.toThrow("Image scan failed");
  });
});

describe("scanQr", () => {
  beforeEach(() => vi.unstubAllGlobals());

  it("returns a ScanResult on success", async () => {
    const rawQr = { ...RAW_SCAN, input_type: "qr" };
    mockFetch(rawQr);

    const file = new File(["data"], "qr.png", { type: "image/png" });
    const result = await scanQr(file);
    expect(result.inputType).toBe("qr");
  });

  it("throws on error", async () => {
    mockFetch({ detail: "QR scan failed" }, 501);
    const file = new File(["data"], "qr.png", { type: "image/png" });
    await expect(scanQr(file)).rejects.toThrow("QR scan failed");
  });
});

describe("listScans", () => {
  beforeEach(() => vi.unstubAllGlobals());

  it("returns paginated scan list", async () => {
    mockFetch({ scans: [RAW_SCAN], page: 1, limit: 20 });
    const result = await listScans(1, 20);

    expect(result.scans).toHaveLength(1);
    expect(result.scans[0].id).toBe("scan-123");
    expect(result.page).toBe(1);
    expect(result.limit).toBe(20);
  });

  it("throws on list failure", async () => {
    mockFetch({ detail: "Failed to load" }, 500);
    await expect(listScans()).rejects.toThrow("Failed to load");
  });
});
