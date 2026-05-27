import { describe, it, expect, vi, beforeEach } from "vitest";
import { api } from "@/lib/api";

describe("api client", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  it("returns success with data on 200 response", async () => {
    const payload = { id: "abc", risk_level: "low" };
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify(payload), { status: 200 })
    );

    const result = await api.get("/api/v1/test");
    expect(result.success).toBe(true);
    expect(result.data).toEqual(payload);
    expect(result.error).toBeNull();
  });

  it("returns failure with error message on 4xx response with JSON detail", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: "Rate limit exceeded" }), {
        status: 429,
        statusText: "Too Many Requests",
      })
    );

    const result = await api.get("/api/v1/test");
    expect(result.success).toBe(false);
    expect(result.data).toBeNull();
    expect(result.error).toBe("Rate limit exceeded");
  });

  it("falls back to statusText when error response has no JSON body", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response("", { status: 503, statusText: "Service Unavailable" })
    );

    const result = await api.get("/api/v1/test");
    expect(result.success).toBe(false);
    expect(result.error).toBe("Service Unavailable");
  });

  it("sends JSON body and Content-Type on POST", async () => {
    const payload = { id: "xyz" };
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify(payload), { status: 200 })
    );

    await api.post("/api/v1/scan/url", { url: "https://example.com" });

    const [, init] = vi.mocked(fetch).mock.calls[0];
    expect((init as RequestInit).method).toBe("POST");
    expect(
      ((init as RequestInit).headers as Record<string, string>)["Content-Type"]
    ).toBe("application/json");
    expect((init as RequestInit).body).toBe(JSON.stringify({ url: "https://example.com" }));
  });

  it("sends FormData without Content-Type header on postForm", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ id: "xyz" }), { status: 200 })
    );

    const form = new FormData();
    form.append("file", new Blob(["data"]), "test.png");
    await api.postForm("/api/v1/scan/image", form);

    const [, init] = vi.mocked(fetch).mock.calls[0];
    expect((init as RequestInit).method).toBe("POST");
    expect(
      ((init as RequestInit).headers as Record<string, string>)?.["Content-Type"]
    ).toBeUndefined();
    expect((init as RequestInit).body).toBeInstanceOf(FormData);
  });
});
