"use client";

import { useEffect, useState } from "react";
import { theme } from "@/lib/theme";
import { Card } from "@/components/ui/Card";

interface ErrorEntry {
  ts: number;
  code: string;
  detail: string;
}

export function ErrorLog() {
  const [errors, setErrors] = useState<ErrorEntry[]>([]);

  useEffect(() => {
    fetch("/health")
      .then((r) => r.json())
      .then((d) => {
        if (d.errors?.length) {
          setErrors((prev) => {
            const merged = [...prev];
            for (const err of d.errors) {
              merged.push({ ts: Date.now(), code: "HEALTH", detail: err });
            }
            return merged.slice(-20);
          });
        }
      })
      .catch(() => {});
    const i = setInterval(() => {
      fetch("/health").then((r) => r.json()).then((d) => {
        if (d.errors?.length) {
          setErrors((prev) => {
            const merged = [...prev];
            for (const err of d.errors) {
              merged.push({ ts: Date.now(), code: "HEALTH", detail: err });
            }
            return merged.slice(-20);
          });
        }
      }).catch(() => {});
    }, 10_000);
    return () => clearInterval(i);
  }, []);

  return (
    <Card title="⚠️ Errores Recientes">
      {errors.length === 0 ? (
        <p className={theme.colors.textMuted}>Sin errores</p>
      ) : (
        <div className="space-y-1 max-h-60 overflow-y-auto">
          {errors.map((e, i) => (
            <div key={i} className="bg-[#da3633]/10 border border-[#da3633]/20 rounded p-2 text-xs">
              <span className="text-[#f85149] font-medium">{e.code}</span>
              <span className="text-[#8b949e] ml-2">{new Date(e.ts).toLocaleTimeString()}</span>
              <p className="text-[#c9d1d9] mt-0.5">{e.detail}</p>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
