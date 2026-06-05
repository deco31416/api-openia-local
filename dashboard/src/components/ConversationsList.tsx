"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { theme, cn } from "@/lib/theme";
import { Card, Loading } from "./UsageCard";
import type { ConversationInfo } from "@/types/api";

export function ConversationsList() {
  const [convs, setConvs] = useState<ConversationInfo[]>([]);

  useEffect(() => {
    api.conversations()
      .then((d) => setConvs(d.data))
      .catch(() => {});
    const i = setInterval(() => api.conversations().then((d) => setConvs(d.data)).catch(() => {}), 20_000);
    return () => clearInterval(i);
  }, []);

  return (
    <Card title="💬 Conversaciones">
      {convs.length === 0 ? (
        <Loading />
      ) : (
        <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
          {convs.slice(0, 15).map((c) => (
            <div key={c.conversation_id} className={cn(theme.colors.border, "border rounded-lg p-3 text-sm")}>
              <a
                href={c.url}
                target="_blank"
                rel="noopener noreferrer"
                className={cn(theme.colors.accent, "hover:underline font-medium")}
              >
                {c.summary || c.conversation_id.slice(0, 12)}
              </a>
              <div className={cn(theme.colors.textMuted, "text-xs mt-1 flex gap-3")}>
                <span>{c.model}</span>
                <span>{(c.total_tokens || 0).toLocaleString()} tokens</span>
                <span>{new Date((c.last_used_at || 0) * 1000).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
