"use client";

import { theme, cn } from "@/lib/theme";
import { Cpu, Check, Zap, Rocket, Brain, Sparkles } from "lucide-react";
import { Card, Stat } from "@/components/ui/Card";

interface ModelInfo {
  id: string;
  label: string;
  icon: React.ReactNode;
}

const MODELS: ModelInfo[] = [
  { id: "o3-5.5-thinking", label: "o3 5.5 Thinking", icon: <Brain className="w-4 h-4 text-purple-400" /> },
  { id: "o3-5.5-instant", label: "o3 5.5 Instant", icon: <Zap className="w-4 h-4 text-yellow-400" /> },
];

interface ModelSelectorProps {
  current: string;
  onChange: (model: string) => void;
}

export function ModelSelector({ current, onChange }: ModelSelectorProps) {
  return (
    <Card title={<><Cpu className="w-5 h-5 text-yellow-400" /><span>Modelo Activo</span></>}>
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
            {m.icon}
            <span>{m.label}</span>
            {current === m.id && <Check className="w-4 h-4 ml-auto text-green-400" />}
          </button>
        ))}
      </div>
      <div className="mt-3 pt-3 border-t border-[#30363d]">
        <Stat label="Modelo actual" value={current} />
      </div>
    </Card>
  );
}
