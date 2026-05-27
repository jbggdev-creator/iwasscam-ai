import { describe, it, expect } from "vitest";
import { urlScanSchema, textScanSchema, phoneScanSchema } from "@/lib/validations/scan";

describe("urlScanSchema", () => {
  it("accepts a valid http URL", () => {
    const result = urlScanSchema.safeParse({ url: "http://example.com" });
    expect(result.success).toBe(true);
  });

  it("accepts a valid https URL", () => {
    const result = urlScanSchema.safeParse({ url: "https://suspicious-shop.com/checkout" });
    expect(result.success).toBe(true);
  });

  it("rejects a non-URL string", () => {
    const result = urlScanSchema.safeParse({ url: "not a url" });
    expect(result.success).toBe(false);
    expect(result.error?.issues[0]?.message).toBe("Please enter a valid URL");
  });

  it("rejects an empty string", () => {
    const result = urlScanSchema.safeParse({ url: "" });
    expect(result.success).toBe(false);
  });

  it("rejects a URL over 2048 characters", () => {
    const longUrl = "https://example.com/" + "a".repeat(2040);
    const result = urlScanSchema.safeParse({ url: longUrl });
    expect(result.success).toBe(false);
    expect(result.error?.issues[0]?.message).toBe("URL is too long");
  });

  it("accepts a URL exactly 2048 characters", () => {
    const url = "https://example.com/" + "a".repeat(2048 - 20);
    const result = urlScanSchema.safeParse({ url });
    expect(result.success).toBe(true);
  });
});

describe("textScanSchema", () => {
  it("accepts a valid scenario", () => {
    const result = textScanSchema.safeParse({
      scenario: "A recruiter asked me to pay ₱500 before my first day.",
    });
    expect(result.success).toBe(true);
  });

  it("rejects input shorter than 10 characters", () => {
    const result = textScanSchema.safeParse({ scenario: "too short" });
    expect(result.success).toBe(false);
    expect(result.error?.issues[0]?.message).toContain("10 characters");
  });

  it("rejects input over 2000 characters", () => {
    const result = textScanSchema.safeParse({ scenario: "a".repeat(2001) });
    expect(result.success).toBe(false);
    expect(result.error?.issues[0]?.message).toContain("2000 characters");
  });

  it("accepts input exactly 10 characters", () => {
    const result = textScanSchema.safeParse({ scenario: "exactly 10" });
    expect(result.success).toBe(true);
  });

  it("accepts input exactly 2000 characters", () => {
    const result = textScanSchema.safeParse({ scenario: "a".repeat(2000) });
    expect(result.success).toBe(true);
  });
});

describe("phoneScanSchema", () => {
  it("accepts a valid Philippine mobile number", () => {
    const result = phoneScanSchema.safeParse({ phone: "+639171234567" });
    expect(result.success).toBe(true);
  });

  it("accepts a number with spaces and dashes", () => {
    const result = phoneScanSchema.safeParse({ phone: "+63 917 123-4567" });
    expect(result.success).toBe(true);
  });

  it("rejects a number shorter than 7 characters", () => {
    const result = phoneScanSchema.safeParse({ phone: "12345" });
    expect(result.success).toBe(false);
  });

  it("rejects letters in the phone number", () => {
    const result = phoneScanSchema.safeParse({ phone: "0917-ABC-DEFG" });
    expect(result.success).toBe(false);
    expect(result.error?.issues[0]?.message).toContain("digits");
  });

  it("rejects a number over 20 characters", () => {
    const result = phoneScanSchema.safeParse({ phone: "1".repeat(21) });
    expect(result.success).toBe(false);
  });
});
