import { NextRequest, NextResponse } from "next/server";

// All dashboard pages are publicly reachable.
// /history and /settings show a locked overlay client-side when not signed in
// instead of hard-redirecting — so users stay in the app flow.
export function middleware(_request: NextRequest) {
  return NextResponse.next();
}

export const config = {
  matcher: [],
};
