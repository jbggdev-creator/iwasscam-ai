export type RiskLevel = "low" | "medium" | "high" | "critical";

export type InputType = "url" | "image" | "text" | "qr";

export interface ScanResult {
  id: string;
  inputType: InputType;
  riskLevel: RiskLevel;
  confidenceScore: number;
  explanation: string;
  findings: Finding[];
  createdAt: string;
}

export interface Finding {
  id: string;
  findingType: string;
  description: string;
  severity: RiskLevel;
}
