"use client";

import { useState } from "react";
import Link from "next/link";
import { ShieldCheck, Menu, X } from "lucide-react";

const NAV_LINKS = [
  { href: "/features", label: "Features" },
  { href: "/scam-education", label: "Scam Education" },
  { href: "/pricing", label: "Pricing" },
] as const;

export function PublicNav() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 h-16">
        <Link href="/" className="flex items-center gap-2 font-bold text-lg text-foreground">
          <ShieldCheck className="h-5 w-5 text-primary" aria-hidden />
          IwasScam AI
        </Link>

        <div className="hidden md:flex items-center gap-6">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              {link.label}
            </Link>
          ))}
        </div>

        <div className="hidden md:flex items-center gap-3">
          <Link
            href="/login"
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            Sign In
          </Link>
          <Link
            href="/scanner"
            className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90 transition-opacity"
          >
            Start Scanning
          </Link>
        </div>

        <button
          className="md:hidden rounded-lg p-2 text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
          onClick={() => setOpen((v) => !v)}
          aria-label={open ? "Close menu" : "Open menu"}
          aria-expanded={open}
        >
          {open ? <X className="h-5 w-5" aria-hidden /> : <Menu className="h-5 w-5" aria-hidden />}
        </button>
      </nav>

      {open && (
        <div className="md:hidden border-t border-border bg-background px-4 py-4 space-y-3">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              onClick={() => setOpen(false)}
              className="block text-sm text-muted-foreground hover:text-foreground py-1 transition-colors"
            >
              {link.label}
            </Link>
          ))}
          <div className="pt-3 border-t border-border flex flex-col gap-2">
            <Link
              href="/login"
              onClick={() => setOpen(false)}
              className="block text-sm font-medium text-center rounded-lg border border-border py-2 hover:bg-muted transition-colors"
            >
              Sign In
            </Link>
            <Link
              href="/scanner"
              onClick={() => setOpen(false)}
              className="block text-sm font-medium text-center rounded-lg bg-primary py-2 text-primary-foreground hover:opacity-90 transition-opacity"
            >
              Start Scanning
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
