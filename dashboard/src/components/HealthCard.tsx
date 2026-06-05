"use client";

import { useEffect, useState } from "react";
import { Heart, ShieldCheck, ShieldAlert, ShieldX, Check, AlertTriangle, X } from "lucide-react";
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

  if (error) return <Card title={<><ShieldX className="w-5 h-5 text-red-400" /><span>Health</span></>}><p className={theme.colors.danger}>{error}</p></Card>;
  if (!data) return <Card title={<><Heart className="w-5 h-5 text-blue-400" /><span>Health</span></>}><Loading /></Card>;

  const statusIcon = data.status === "healthy"
    ? <ShieldCheck className="w-4 h-4 text-green-400" />
    : data.status === "degraded"
    ? <ShieldAlert className="w-4 h-4 text-yellow-400" />
    : <ShieldX className="w-4 h-4 text-red-400" />;

  return (
    <Card title={<><Heart className="w-5 h-5 text-blue-400" /><span>Health</span></>}>
      <Stat label="Estado" value={<span className="inline-flex items-center gap-1">{statusIcon}{data.status}</span>} />
      <Stat label="Auth" value={data.authenticated ? <Check className="w-4 h-4 text-green-400" /> : <X className="w-4 h-4 text-red-400" />} />
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
