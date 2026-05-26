import { api } from "./api";
import type { ScanResult } from "@/types/scan";

interface RawFinding {
  id: string;
  finding_type: string;
  description: string;
  severity: string;
}

interface RawScanResponse {
  id: string;
  input_type: string;
  risk_level: string;
  confidence_score: number;
  explanation: string;
  findings: RawFinding[];
  created_at: string;
}

function toScanResult(raw: RawScanResponse): ScanResult {
  return {
    id: raw.id,
    inputType: raw.input_type as ScanResult["inputType"],
    riskLevel: raw.risk_level as ScanResult["riskLevel"],
    confidenceScore: raw.confidence_score,
    explanation: raw.explanation,
    findings: raw.findings.map((f) => ({
      id: f.id,
      findingType: f.finding_type,
      description: f.description,
      severity: f.severity as ScanResult["riskLevel"],
    })),
    createdAt: raw.created_at,
  };
}

export async function scanUrl(url: string): Promise<ScanResult> {
  const response = await api.post<RawScanResponse>("/api/v1/scan/url", { url });
  if (!response.success || !response.data) {
    throw new Error(response.error ?? "URL scan failed");
  }
  return toScanResult(response.data);
}

export async function scanText(scenario: string): Promise<ScanResult> {
  const response = await api.post<RawScanResponse>("/api/v1/scan/text", { scenario });
  if (!response.success || !response.data) {
    throw new Error(response.error ?? "Text scan failed");
  }
  return toScanResult(response.data);
}

export async function scanImage(file: File): Promise<ScanResult> {
  const form = new FormData();
  form.append("file", file);
  const response = await api.postForm<RawScanResponse>("/api/v1/scan/image", form);
  if (!response.success || !response.data) {
    throw new Error(response.error ?? "Image scan failed");
  }
  return toScanResult(response.data);
}

export async function scanQr(file: File): Promise<ScanResult> {
  const form = new FormData();
  form.append("file", file);
  const response = await api.postForm<RawScanResponse>("/api/v1/scan/qr", form);
  if (!response.success || !response.data) {
    throw new Error(response.error ?? "QR scan failed");
  }
  return toScanResult(response.data);
}

export async function getScan(id: string): Promise<ScanResult> {
  const response = await api.get<RawScanResponse>(`/api/v1/scan/${id}`);
  if (!response.success || !response.data) {
    throw new Error(response.error ?? "Scan not found");
  }
  return toScanResult(response.data);
}

interface RawScanListResponse {
  scans: RawScanResponse[];
  page: number;
  limit: number;
}

export interface ScanListResult {
  scans: ScanResult[];
  page: number;
  limit: number;
}

export async function listScans(page = 1, limit = 20): Promise<ScanListResult> {
  const response = await api.get<RawScanListResponse>(
    `/api/v1/scan?page=${page}&limit=${limit}`
  );
  if (!response.success || !response.data) {
    throw new Error(response.error ?? "Failed to load scan history");
  }
  return {
    scans: response.data.scans.map(toScanResult),
    page: response.data.page,
    limit: response.data.limit,
  };
}
