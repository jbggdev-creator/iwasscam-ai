"use client";

import { useState, useRef, useCallback } from "react";
import { Loader2, Upload, ImageIcon, X } from "lucide-react";
import { scanImage } from "@/lib/scan";
import { ScanResult } from "./ScanResult";
import type { ScanResult as ScanResultType } from "@/types/scan";

const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"] as const;
const MAX_SIZE_BYTES = 10 * 1024 * 1024;

function validateFile(file: File): string | null {
  if (!ALLOWED_TYPES.includes(file.type as (typeof ALLOWED_TYPES)[number])) {
    return "Only JPEG, PNG, and WebP images are accepted";
  }
  if (file.size > MAX_SIZE_BYTES) {
    return "Image must be under 10 MB";
  }
  return null;
}

export function ImageScanForm() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ScanResultType | null>(null);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((selected: File) => {
    const validationError = validateFile(selected);
    if (validationError) {
      setError(validationError);
      return;
    }
    setError(null);
    setResult(null);
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);
      const dropped = e.dataTransfer.files[0];
      if (dropped) handleFile(dropped);
    },
    [handleFile]
  );

  function clearFile() {
    if (preview) URL.revokeObjectURL(preview);
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
    if (inputRef.current) inputRef.current.value = "";
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!file) return;

    setError(null);
    setResult(null);
    setIsLoading(true);

    try {
      const scanResult = await scanImage(file);
      setResult(scanResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        {!file ? (
          <div
            role="button"
            tabIndex={0}
            aria-label="Upload screenshot — click or drag and drop"
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            onClick={() => inputRef.current?.click()}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
            }}
            className={[
              "flex flex-col items-center justify-center rounded-xl border-2 border-dashed",
              "p-10 text-center transition-colors cursor-pointer select-none",
              isDragging
                ? "border-primary bg-primary/5"
                : "border-border hover:border-primary/50 hover:bg-muted/30",
            ].join(" ")}
          >
            <Upload className="mb-3 h-8 w-8 text-muted-foreground" aria-hidden />
            <p className="text-sm font-medium text-foreground">
              Drop screenshot here or{" "}
              <span className="text-primary underline underline-offset-2">browse</span>
            </p>
            <p className="mt-1 text-xs text-muted-foreground">JPEG, PNG, or WebP — max 10 MB</p>
          </div>
        ) : (
          <div className="relative rounded-xl border border-border overflow-hidden">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={preview!}
              alt="Selected screenshot preview"
              className="w-full object-contain max-h-64 bg-muted"
            />
            <button
              type="button"
              onClick={clearFile}
              aria-label="Remove selected image"
              className="absolute right-2 top-2 rounded-full bg-background/90 p-1.5 shadow-sm hover:bg-background border border-border transition-colors"
            >
              <X className="h-4 w-4 text-foreground" />
            </button>
            <div className="px-4 py-2.5 border-t border-border bg-card">
              <p className="text-sm font-medium text-foreground truncate">{file.name}</p>
              <p className="text-xs text-muted-foreground">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>
        )}

        <input
          ref={inputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          className="sr-only"
          aria-hidden
          tabIndex={-1}
          onChange={(e) => {
            const selected = e.target.files?.[0];
            if (selected) handleFile(selected);
          }}
        />

        {error && (
          <p role="alert" className="text-sm text-destructive">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={isLoading || !file}
          className="inline-flex w-full sm:w-auto items-center justify-center gap-2 rounded-lg bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
          ) : (
            <ImageIcon className="h-4 w-4" aria-hidden />
          )}
          {isLoading ? "Analyzing…" : "Analyze Screenshot"}
        </button>
      </form>

      {result && <ScanResult result={result} />}
    </div>
  );
}
