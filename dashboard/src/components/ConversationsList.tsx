"use client";

import { useEffect, useState } from "react";
import { MessagesSquare, ExternalLink } from "lucide-react";
import { theme, cn } from "@/lib/theme";
import { Card, Loading } from "@/components/ui/Card";
import type { ConversationInfo } from "@/types/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:9090";

export function ConversationsList() {
  const [convs, setConvs] = useState<ConversationInfo[]>([]);

  useEffect(() => {
    fetch(`${API_BASE}/v1/conversations`)
      .then((r) => r.json())
      .then((d) => setConvs(d.data || []))
      .catch(() => {});
    const i = setInterval(() => fetch(`${API_BASE}/v1/conversations`).then((r) => r.json()).then((d) => setConvs(d.data || [])).catch(() => {}), 20_000);
    return () => clearInterval(i);
  }, []);

  return (
    <Card title={<><MessagesSquare className="w-5 h-5 text-purple-400" /><span>Conversaciones</span></>}>
      {convs.length === 0 ? (
        <Loading />
      ) : (
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {convs.slice(0, 10).map((c) => (
            <div key={c.conversation_id} className={cn(theme.colors.border, "border rounded-lg p-2.5 text-sm")}>
              <a
                href={c.url}
                target="_blank"
                rel="noopener noreferrer"
                className={cn(theme.colors.accent, "hover:underline font-medium")}
              >
                {c.summary || c.conversation_id.slice(0, 12)}
              </a>
              <div className={cn(theme.colors.textMuted, "text-xs mt-1 flex gap-2")}>
                <span>{c.model}</span>
                <span>{(c.total_tokens || 0).toLocaleString()} tokens</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
