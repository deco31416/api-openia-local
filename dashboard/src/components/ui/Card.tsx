"use client";

import { theme, cn } from "@/lib/theme";
import type { ReactNode } from "react";

export function Card({ title, children }: { title: ReactNode; children: React.ReactNode }) {
  return (
    <div className={cn(theme.colors.card, theme.colors.border, theme.layout.card)}>
      <h2 className={cn(theme.colors.accent, "text-lg font-semibold mb-3 pb-2 border-b flex items-center gap-2", theme.colors.border)}>
        {title}
      </h2>
      {children}
    </div>
  );
}

export function Stat({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className={theme.layout.stat}>
      <span className={theme.colors.textMuted}>{label}</span>
      <span className="font-semibold inline-flex items-center">{value}</span>
    </div>
  );
}

export function Loading() {
  return <p className={theme.colors.textMuted}>Cargando...</p>;
}
