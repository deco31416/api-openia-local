"use client";

import { useEffect, useState } from "react";
import { theme, cn } from "@/lib/theme";
import { Card, Stat, Loading } from "@/components/ui/Card";
import type { HealthResponse } from "@/types/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:9090";

export function HealthCard() {
  const [data, setData] = useState<HealthResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then((r) => r.json())
      .then(setData)
      .catch((e) => setError(e.message));
    const i = setInterval(() => fetch(`${API_BASE}/health`).then((r) => r.json()).then(setData).catch(() => {}), 10_000);
    return () => clearInterval(i);
  }, []);

  if (error) return <Card title="🩺 Health"><p className={theme.colors.danger}>{error}</p></Card>;
  if (!data) return <Card title="🩺 Health"><Loading /></Card>;

  const statusIcon = data.status === "healthy" ? "✅" : data.status === "degraded" ? "⚠️" : "❌";

  return (
    <Card title="🩺 Health">
      <Stat label="Estado" value={`${statusIcon} ${data.status}`} />
      <Stat label="Auth" value={data.authenticated ? "✅" : "❌"} />
      <Stat label="Uptime" value={`${Math.floor(data.uptime_seconds)}s`} />
      <hr className={cn(theme.colors.border, "my-2")} />
      {data.components?.slice(0, 10).map((c) => (
        <Stat
          key={c.name}
          label={c.name}
          value={c.status === "ok" ? "✅" : c.status === "error" ? "❌" : "⚠️"}
        />
      ))}
    </Card>
  );
}
