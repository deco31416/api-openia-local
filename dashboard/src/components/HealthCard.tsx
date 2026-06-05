"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { theme, cn } from "@/lib/theme";
import type { HealthResponse } from "@/types/api";

export function HealthCard() {
  const [data, setData] = useState<HealthResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.health()
      .then(setData)
      .catch((e) => setError(e.message));
    const i = setInterval(() => api.health().then(setData).catch(() => {}), 10_000);
    return () => clearInterval(i);
  }, []);

  if (error) return <Card title="🩺 Health"><p className={theme.colors.danger}>{error}</p></Card>;
  if (!data) return <Card title="🩺 Health"><p className={theme.colors.textMuted}>Cargando...</p></Card>;

  const statusIcon = data.status === "healthy" ? "✅" : data.status === "degraded" ? "⚠️" : "❌";

  return (
    <Card title="🩺 Health">
      <Stat label="Estado" value={`${statusIcon} ${data.status}`} />
      <Stat label="Auth" value={data.authenticated ? "✅" : "❌"} />
      <Stat label="Uptime" value={`${Math.floor(data.uptime_seconds)}s`} />
      <Stat label="Versión" value={data.version} />
      <hr className={cn(theme.colors.border, "my-2")} />
      {data.components?.slice(0, 8).map((c) => (
        <Stat
          key={c.name}
          label={c.name}
          value={c.status === "ok" ? "✅" : c.status === "error" ? "❌" : "⚠️"}
        />
      ))}
    </Card>
  );
}

// ─── Sub-componentes internos ───

function Card({ title, children }: { title: string; children: React.ReactNode }) {
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
      <span className="font-semibold">{value}</span>
    </div>
  );
}
