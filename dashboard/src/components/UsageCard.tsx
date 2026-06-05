"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { theme, cn } from "@/lib/theme";
import type { UsageResponse } from "@/types/api";

export function UsageCard() {
  const [data, setData] = useState<UsageResponse | null>(null);

  useEffect(() => {
    api.usage().then(setData).catch(() => {});
    const i = setInterval(() => api.usage().then(setData).catch(() => {}), 15_000);
    return () => clearInterval(i);
  }, []);

  if (!data) return <Card title="📊 Uso Global"><Loading /></Card>;

  const t = data.totals;

  return (
    <Card title="📊 Uso Global">
      <Stat label="Tokens subida" value={t.prompt_tokens.toLocaleString()} />
      <Stat label="Tokens bajada" value={t.completion_tokens.toLocaleString()} />
      <Stat label="Total tokens" value={t.total_tokens.toLocaleString()} />
      <Stat label="Costo USD" value={`$${t.cost_total_usd.toFixed(4)}`} />
      <Stat label="Llamadas" value={t.calls.toString()} />
      <hr className={cn(theme.colors.border, "my-2")} />
      <p className={cn(theme.colors.textMuted, "text-xs mb-1")}>Por modelo:</p>
      {Object.entries(data.by_model).slice(0, 5).map(([model, m]) => (
        <Stat key={model} label={model} value={`$${m.cost_total_usd.toFixed(4)}`} />
      ))}
    </Card>
  );
}

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

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className={theme.layout.stat}>
      <span className={theme.colors.textMuted}>{label}</span>
      <span className={cn("font-semibold", value.startsWith("$") ? theme.colors.success : "")}>{value}</span>
    </div>
  );
}

export function Loading() {
  return <p className={theme.colors.textMuted}>Cargando...</p>;
}
