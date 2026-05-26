"use client";

import * as Tabs from "@radix-ui/react-tabs";
import { Link2, ImageIcon, MessageSquare, QrCode, ShieldAlert } from "lucide-react";
import { UrlScanForm } from "@/components/scanner/UrlScanForm";
import { ImageScanForm } from "@/components/scanner/ImageScanForm";
import { TextScanForm } from "@/components/scanner/TextScanForm";
import { QrScanForm } from "@/components/scanner/QrScanForm";

const tabTriggerClass = [
  "flex flex-1 items-center justify-center gap-1.5",
  "rounded-lg px-2 sm:px-3 py-2 text-xs font-medium",
  "transition-all cursor-pointer select-none outline-none",
  "text-muted-foreground hover:text-foreground",
  "data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm",
  "focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1",
].join(" ");

export default function ScannerPage() {
  return (
    <main className="mx-auto max-w-2xl px-4 py-8 space-y-6">
      <header className="space-y-1.5">
        <div className="flex items-center gap-2.5">
          <ShieldAlert className="h-6 w-6 text-primary flex-shrink-0" aria-hidden />
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Scam Scanner</h1>
        </div>
        <p className="text-sm text-muted-foreground leading-relaxed">
          AI-powered analysis to detect scams, phishing, and fraud. Powered by Philippine threat
          intelligence and real-time risk scoring.
        </p>
      </header>

      <Tabs.Root defaultValue="url">
        <Tabs.List
          aria-label="Choose how to scan"
          className="flex rounded-xl bg-muted p-1 gap-0.5"
        >
          <Tabs.Trigger value="url" className={tabTriggerClass}>
            <Link2 className="h-3.5 w-3.5 flex-shrink-0" aria-hidden />
            <span>URL</span>
          </Tabs.Trigger>

          <Tabs.Trigger value="screenshot" className={tabTriggerClass}>
            <ImageIcon className="h-3.5 w-3.5 flex-shrink-0" aria-hidden />
            <span className="hidden sm:inline">Screenshot</span>
            <span className="sm:hidden">Image</span>
          </Tabs.Trigger>

          <Tabs.Trigger value="qr" className={tabTriggerClass}>
            <QrCode className="h-3.5 w-3.5 flex-shrink-0" aria-hidden />
            <span className="hidden sm:inline">QR Code</span>
            <span className="sm:hidden">QR</span>
          </Tabs.Trigger>

          <Tabs.Trigger value="ask-ai" className={tabTriggerClass}>
            <MessageSquare className="h-3.5 w-3.5 flex-shrink-0" aria-hidden />
            <span className="hidden sm:inline">Ask AI</span>
            <span className="sm:hidden">AI</span>
          </Tabs.Trigger>
        </Tabs.List>

        <Tabs.Content value="url" className="mt-5 space-y-4">
          <p className="text-sm text-muted-foreground">
            Paste a suspicious link to check for phishing attempts, fake domains, and scam websites.
          </p>
          <UrlScanForm />
        </Tabs.Content>

        <Tabs.Content value="screenshot" className="mt-5 space-y-4">
          <p className="text-sm text-muted-foreground">
            Upload a screenshot of a suspicious message, GCash receipt, or Facebook Marketplace
            conversation for AI analysis.
          </p>
          <ImageScanForm />
        </Tabs.Content>

        <Tabs.Content value="qr" className="mt-5 space-y-4">
          <p className="text-sm text-muted-foreground">
            Upload a QR code image to decode its destination and check for malicious links,
            phishing redirects, or suspicious content.
          </p>
          <QrScanForm />
        </Tabs.Content>

        <Tabs.Content value="ask-ai" className="mt-5 space-y-4">
          <p className="text-sm text-muted-foreground">
            Describe a suspicious situation in your own words — our AI will identify red flags and
            social engineering tactics.
          </p>
          <TextScanForm />
        </Tabs.Content>
      </Tabs.Root>
    </main>
  );
}
