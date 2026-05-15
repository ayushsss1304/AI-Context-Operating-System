import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Context OS",
  description: "Shared memory and workflow continuity for AI-native teams"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
