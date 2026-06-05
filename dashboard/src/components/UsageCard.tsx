"use client";

import { useEffect, useState } from "react";
import { BarChart3, DollarSign } from "lucide-react";
import { theme, cn } from "@/lib/theme";
import { Card, Stat, Loading } from "@/components/ui/Card";
import type { UsageResponse } from "@/types/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:9090";

export function UsageCard() {
  const [data, setData] = useState<UsageResponse | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/v1/usage`).then((r) => r.json()).then(setData).catch(() => {});
    const i = setInterval(() => fetch(`${API_BASE}/v1/usage`).then((r) => r.json()).then(setData).catch(() => {}), 15_000);
    return () => clearInterval(i);
  }, []);

  if (!data) return <Card title={<><BarChart3 className="w-5 h-5 text-green-400" /><span>Uso Global</span></>}><Loading /></Card>;

  const t = data.totals;

  return (
    <Card title={<><BarChart3 className="w-5 h-5 text-green-400" /><span>Uso Global</span></>}>
      <Stat label="Tokens subida" value={t.prompt_tokens.toLocaleString()} />
      <Stat label="Tokens bajada" value={t.completion_tokens.toLocaleString()} />
      <Stat label="Total tokens" value={t.total_tokens.toLocaleString()} />
      <Stat label="Costo USD" value={<span className="inline-flex items-center gap-1 text-green-400"><DollarSign className="w-3.5 h-3.5" />{t.cost_total_usd.toFixed(4)}</span>} />
      <Stat label="Llamadas" value={t.calls.toString()} />
      <hr className={cn(theme.colors.border, "my-2")} />
      <p className={cn(theme.colors.textMuted, "text-xs mb-1")}>Por modelo:</p>
      {Object.entries(data.by_model).slice(0, 5).map(([model, m]) => (
        <Stat key={model} label={model} value={<span className="inline-flex items-center gap-1 text-green-400"><DollarSign className="w-3 h-3" />{m.cost_total_usd.toFixed(4)}</span>} />
      ))}
    </Card>
  );
}
