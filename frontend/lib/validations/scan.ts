import { z } from "zod";

export const urlScanSchema = z.object({
  url: z
    .string()
    .url("Please enter a valid URL")
    .max(2048, "URL is too long"),
});

export const textScanSchema = z.object({
  scenario: z
    .string()
    .min(10, "Please describe the scenario in at least 10 characters")
    .max(2000, "Description must be under 2000 characters"),
});

export const phoneScanSchema = z.object({
  phone: z
    .string()
    .min(7, "Enter a valid phone number")
    .max(20, "Phone number is too long")
    .regex(/^[+\d\s\-().]+$/, "Enter digits, spaces, +, -, or ( ) only"),
});

export type UrlScanInput = z.infer<typeof urlScanSchema>;
export type TextScanInput = z.infer<typeof textScanSchema>;
export type PhoneScanInput = z.infer<typeof phoneScanSchema>;
