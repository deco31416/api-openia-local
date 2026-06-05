"use client";

import { useEffect, useState } from "react";
import { Navbar } from "@/components/Navbar";
import { HealthCard } from "@/components/HealthCard";
import { UsageCard } from "@/components/UsageCard";
import { ConversationsList } from "@/components/ConversationsList";
import { QueuePanel } from "@/components/QueuePanel";
import { ModelSelector } from "@/components/ModelSelector";
import { ChatBox } from "@/components/ChatBox";
import { ErrorLog } from "@/components/ErrorLog";
import { theme, cn } from "@/lib/theme";
import type { HealthResponse } from "@/types/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:9090";

export default function DashboardPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [model, setModel] = useState("gpt-4o");

  useEffect(() => {
    fetch(`${API_BASE}/health`).then((r) => r.json()).then(setHealth).catch(() => {});
    const i = setInterval(() => fetch(`${API_BASE}/health`).then((r) => r.json()).then(setHealth).catch(() => {}), 10_000);
    return () => clearInterval(i);
  }, []);

  const handleChat = async (message: string, mdl: string, skill: string): Promise<string> => {
    const res = await fetch(`${API_BASE}/v1/agent/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Skill": skill,
      },
      body: JSON.stringify({ model: mdl, messages: [{ role: "user", content: message }] }),
    });
    const data = await res.json();
    return data.choices?.[0]?.message?.content || JSON.stringify(data);
  };

  return (
    <div className={cn(theme.colors.bg, theme.colors.text, "min-h-screen")}>
      <Navbar
        status={health?.status || "unhealthy"}
        version={health?.version || "?.?.?"}
        uptime={health?.uptime_seconds || 0}
      />

      <main className="max-w-7xl mx-auto p-4 md:p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          <HealthCard />
          <UsageCard />
          <QueuePanel />
          <ModelSelector current={model} onChange={setModel} />
          <ChatBox onSend={handleChat} />
          <div className="flex flex-col gap-4">
            <ConversationsList />
            <ErrorLog />
          </div>
        </div>
      </main>

      <footer className={cn(theme.colors.textMuted, "text-center text-xs py-4 border-t", theme.colors.border)}>
        v{health?.version || "?.?.?"} · Auto-refresh · © 2026 deco31416.com
      </footer>
    </div>
  );
}
