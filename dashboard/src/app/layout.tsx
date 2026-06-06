import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ChatGPT Web Bridge — Dashboard",
  description: "Dashboard local para monitoreo del bridge",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" className="dark">
      <body className="antialiased flex flex-col min-h-screen">{children}</body>
    </html>
  );
}
