"use client";

import { theme, cn } from "@/lib/theme";

export function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className={cn(theme.colors.card, theme.colors.border, theme.layout.card)}>
      <h2 className={cn(theme.colors.accent, "text-lg font-semibold mb-3 pb-2 border-b", theme.colors.border)}>
        {title}
      </h2>
      {children}
    </div>
  );
}

export function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className={theme.layout.stat}>
      <span className={theme.colors.textMuted}>{label}</span>
      <span className="font-semibold">{value}</span>
    </div>
  );
}

export function Loading() {
  return <p className={theme.colors.textMuted}>Cargando...</p>;
}
