import { PublicNav } from "@/components/shared/PublicNav";

export default function PublicLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <PublicNav />
      {children}
      <footer className="border-t border-border bg-muted/30 mt-16">
        <div className="mx-auto max-w-6xl px-4 py-10 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
          <p>© {new Date().getFullYear()} IwasScam AI. Protecting Filipinos from online fraud.</p>
          <div className="flex gap-5">
            <a href="/privacy" className="hover:text-foreground transition-colors">Privacy</a>
            <a href="/terms" className="hover:text-foreground transition-colors">Terms</a>
            <a href="/scam-education" className="hover:text-foreground transition-colors">Scam Education</a>
          </div>
        </div>
      </footer>
    </>
  );
}
