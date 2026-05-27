import { redirect } from "next/navigation";
import { headers } from "next/headers";
import { auth } from "@/lib/auth-server";
import { DashboardNav } from "@/components/shared/DashboardNav";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) {
    redirect("/login");
  }

  return (
    <>
      <DashboardNav />
      {children}
    </>
  );
}
