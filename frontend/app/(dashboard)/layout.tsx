import { DashboardNav } from "@/components/shared/DashboardNav";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <DashboardNav />
      {children}
    </>
  );
}
