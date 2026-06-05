"use client";

import { useEffect, useState } from "react";
import { ListOrdered, CheckCircle, AlertCircle } from "lucide-react";
import { theme, cn } from "@/lib/theme";
import { Card, Stat } from "@/components/ui/Card";
import type { QueueStats } from "@/types/api";

export function QueuePanel() {
  const [stats, setStats] = useState<QueueStats>({ pending: 0, processed: 0, rejected: 0 });

  useEffect(() => {
    fetch("/api/queue")
      .then((r) => r.json())
      .then(setStats)
      .catch(() => {});
    const i = setInterval(() => fetch("/api/queue").then((r) => r.json()).then(setStats).catch(() => {}), 5_000);
    return () => clearInterval(i);
  }, []);

  return (
    <Card title={<><ListOrdered className="w-5 h-5 text-orange-400" /><span>Cola de Requests</span></>}>
      <Stat label="En cola" value={stats.pending.toString()} />
      <Stat label="Procesados" value={stats.processed.toLocaleString()} />
      <Stat label="Rechazados" value={stats.rejected.toLocaleString()} />
      <div className="mt-3 pt-3 border-t border-[#30363d]">
        <div className="text-xs text-[#8b949e] mb-1">Estado:</div>
        <span className={cn(
          "inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium",
          stats.pending === 0 ? "bg-[#238636]/20 text-[#7ee787]" :
          stats.pending < 5 ? "bg-[#d29922]/20 text-[#d29922]" :
          "bg-[#da3633]/20 text-[#f85149]"
        )}>
          {stats.pending === 0 ? <><CheckCircle className="w-3 h-3" /> Libre</> : stats.pending < 5 ? <><AlertCircle className="w-3 h-3" /> Ocupada</> : <><AlertCircle className="w-3 h-3" /> Saturada</>}
        </span>
      </div>
    </Card>
  );
}
