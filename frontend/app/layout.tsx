import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "IwasScam AI — Scam Detection for Filipinos",
  description:
    "AI-powered scam detection and trust verification platform. Protect yourself from online fraud in the Philippines.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  );
}
