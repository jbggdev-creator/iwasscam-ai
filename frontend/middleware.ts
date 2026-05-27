import { NextRequest, NextResponse } from "next/server";

const PROTECTED = ["/scanner", "/history", "/settings"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const isProtected = PROTECTED.some((p) => pathname.startsWith(p));

  if (!isProtected) return NextResponse.next();

  // Better Auth stores the session as a signed cookie named "better-auth.session_token".
  // Presence of the cookie is enough to let the layout's server-side session check do
  // the authoritative validation. Absence means definitely not logged in → redirect.
  const session =
    request.cookies.get("better-auth.session_token") ??
    request.cookies.get("__Secure-better-auth.session_token");

  if (!session) {
    const loginUrl = new URL("/login", request.url);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/scanner/:path*", "/history/:path*", "/settings/:path*"],
};
