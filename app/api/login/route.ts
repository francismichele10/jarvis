import { NextRequest, NextResponse } from "next/server";
import { adminAuth } from "@/lib/firebase-admin";

// Lightweight per-instance throttling. Add an edge/WAF rate limit in production too.
const attempts = new Map<string, { count: number; until: number }>();
export async function POST(req: NextRequest) {
  const ip = req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "unknown";
  const now = Date.now(); const current = attempts.get(ip);
  if (current && current.until > now && current.count >= 8) return NextResponse.json({ error: "Too many attempts. Please wait a little and try again." }, { status: 429 });
  try {
    const body = await req.json(); const pin = String(body.pin ?? "");
    if (!/^\\d{4}$/.test(pin)) return NextResponse.json({ error: "Enter your four-digit PIN." }, { status: 400 });
    const francis = process.env.FRANCIS_PIN; const angela = process.env.ANGELA_PIN;
    if (!francis || !angela || francis === angela) return NextResponse.json({ error: "The two private PINs have not been configured correctly." }, { status: 503 });
    const user = pin === francis ? "francis" : pin === angela ? "angela" : null;
    if (!user) { const next = current && current.until > now ? current : { count: 0, until: now + 15 * 60 * 1000 }; attempts.set(ip, { count: next.count + 1, until: next.until }); return NextResponse.json({ error: "That PIN doesn't match. Try again." }, { status: 401 }); }
    attempts.delete(ip);
    const token = await adminAuth().createCustomToken(user, { participant: user });
    return NextResponse.json({ token, user });
  } catch { return NextResponse.json({ error: "Unable to sign in right now. Please try again." }, { status: 500 }); }
}
