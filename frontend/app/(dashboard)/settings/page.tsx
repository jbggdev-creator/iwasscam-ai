"use client";

import { Settings, User, Mail, ShieldCheck } from "lucide-react";
import { useSession } from "@/lib/auth";
import Link from "next/link";

export default function SettingsPage() {
  const { data: session, isPending } = useSession();

  return (
    <main className="mx-auto max-w-2xl px-4 py-8 space-y-6">
      <header className="space-y-1.5">
        <div className="flex items-center gap-2.5">
          <Settings className="h-6 w-6 text-primary flex-shrink-0" aria-hidden />
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Settings</h1>
        </div>
        <p className="text-sm text-muted-foreground">Manage your account and preferences.</p>
      </header>

      {isPending && (
        <div className="rounded-xl border border-border bg-muted/40 h-40 animate-pulse" />
      )}

      {!isPending && !session && (
        <div className="relative">
          {/* blurred fake settings blocks */}
          <div className="space-y-4 blur-sm pointer-events-none select-none" aria-hidden>
            <div className="rounded-xl border border-border bg-card h-40" />
            <div className="rounded-xl border border-border bg-card h-24" />
          </div>
          {/* lock overlay */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="flex flex-col items-center gap-3 rounded-2xl border border-border bg-background/90 px-8 py-7 shadow-lg backdrop-blur-sm text-center">
              <ShieldCheck className="h-8 w-8 text-primary" aria-hidden />
              <p className="text-sm font-semibold text-foreground">Sign in to view your settings</p>
              <p className="text-xs text-muted-foreground max-w-[220px]">
                Create a free account to manage your profile and preferences.
              </p>
              <div className="flex gap-2 pt-1">
                <Link
                  href="/login"
                  className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-foreground hover:bg-muted transition-colors"
                >
                  Sign in
                </Link>
                <Link
                  href="/register"
                  className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90 transition-opacity"
                >
                  Create account
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}

      {!isPending && session && (
        <div className="space-y-4">
          <div className="rounded-xl border border-border bg-card p-6 space-y-4">
            <h2 className="text-base font-semibold text-foreground">Account</h2>

            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10 flex-shrink-0">
                  <User className="h-4 w-4 text-primary" aria-hidden />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Name</p>
                  <p className="text-sm font-medium text-foreground">
                    {session.user.name || "—"}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10 flex-shrink-0">
                  <Mail className="h-4 w-4 text-primary" aria-hidden />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Email</p>
                  <p className="text-sm font-medium text-foreground">{session.user.email}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-card p-6 space-y-3">
            <h2 className="text-base font-semibold text-foreground">Security</h2>
            <p className="text-sm text-muted-foreground">
              Your account is protected with a password. Password change and 2FA are coming soon.
            </p>
          </div>
        </div>
      )}
    </main>
  );
}
