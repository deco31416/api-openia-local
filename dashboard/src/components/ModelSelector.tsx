"use client";

import { theme, cn } from "@/lib/theme";
import { Card, Stat } from "@/components/ui/Card";

interface ModelInfo {
  id: string;
  label: string;
  icon: string;
}

const MODELS: ModelInfo[] = [
  { id: "gpt-4o", label: "GPT-4o", icon: "🧠" },
  { id: "gpt-4o-mini", label: "GPT-4o Mini", icon: "⚡" },
  { id: "o3", label: "o3", icon: "🔮" },
  { id: "o4-mini", label: "o4-mini", icon: "💎" },
  { id: "gpt-4.1", label: "GPT-4.1", icon: "🚀" },
];

interface ModelSelectorProps {
  current: string;
  onChange: (model: string) => void;
}

export function ModelSelector({ current, onChange }: ModelSelectorProps) {
  return (
    <Card title="🤖 Modelo Activo">
      <div className="space-y-1">
        {MODELS.map((m) => (
          <button
            key={m.id}
            onClick={() => onChange(m.id)}
            className={cn(
              "w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all",
              current === m.id
                ? "bg-[#58a6ff]/20 text-[#58a6ff] border border-[#58a6ff]/30 font-semibold"
                : "text-[#8b949e] hover:text-[#c9d1d9] hover:bg-[#30363d]/30"
            )}
          >
            <span className="text-base">{m.icon}</span>
            <span>{m.label}</span>
            {current === m.id && <span className="ml-auto text-xs text-[#7ee787]">✓</span>}
          </button>
        ))}
      </div>
      <div className="mt-3 pt-3 border-t border-[#30363d]">
        <Stat label="Modelo actual" value={current} />
      </div>
    </Card>
  );
}
