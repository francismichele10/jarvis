import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "Between Us — A little space for two", description: "A private, gentle space to talk, check in and share thoughts." };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
