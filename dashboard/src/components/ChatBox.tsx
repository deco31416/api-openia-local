"use client";

import { useState } from "react";
import { theme, cn } from "@/lib/theme";
import { Card } from "@/components/ui/Card";

interface ChatBoxProps {
  onSend: (message: string, model: string, skill: string) => Promise<string>;
  apiKey?: string;
}

export function ChatBox({ onSend, apiKey }: ChatBoxProps) {
  const [message, setMessage] = useState("");
  const [model, setModel] = useState("gpt-4o");
  const [skill, setSkill] = useState("default");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!message.trim() || loading) return;
    setLoading(true);
    setResponse("");
    try {
      const result = await onSend(message, model, skill);
      setResponse(result);
    } catch (e: unknown) {
      setResponse(`Error: ${e instanceof Error ? e.message : "Unknown"}`);
    }
    setLoading(false);
  };

  return (
    <Card title="💬 Chat Rápido">
      <div className="space-y-3">
        {/* Selector de modelo */}
        <div className="flex gap-2">
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-1.5 text-sm text-[#c9d1d9]"
          >
            <option value="gpt-4o">GPT-4o</option>
            <option value="gpt-4o-mini">GPT-4o Mini</option>
            <option value="o3">o3</option>
            <option value="o4-mini">o4-mini</option>
          </select>
          <select
            value={skill}
            onChange={(e) => setSkill(e.target.value)}
            className="bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-1.5 text-sm text-[#c9d1d9]"
          >
            <option value="default">Default</option>
            <option value="code-review">Code Review</option>
            <option value="experto-python">Experto Python</option>
            <option value="explicar-a-ninos">Explicar a niños</option>
          </select>
        </div>

        {/* Input */}
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
          placeholder="Escribe un mensaje... (Enter para enviar)"
          rows={3}
          className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-[#c9d1d9] placeholder-[#484f58] resize-none focus:outline-none focus:border-[#58a6ff]"
        />

        {/* Botón */}
        <button
          onClick={handleSend}
          disabled={loading || !message.trim()}
          className={cn(
            "w-full py-2 rounded-lg text-sm font-medium transition-all",
            loading || !message.trim()
              ? "bg-[#30363d] text-[#484f58] cursor-not-allowed"
              : "bg-[#238636] text-white hover:bg-[#2ea043]"
          )}
        >
          {loading ? "⏳ Enviando..." : "📤 Enviar"}
        </button>

        {/* Respuesta */}
        {response && (
          <div className="bg-[#0d1117] border border-[#30363d] rounded-lg p-3 text-sm max-h-60 overflow-y-auto">
            <pre className="whitespace-pre-wrap text-[#c9d1d9] font-sans">{response}</pre>
          </div>
        )}
      </div>
    </Card>
  );
}
