"use client";

import { useState } from "react";
import {
  LayoutDashboard, Heart, BarChart3, MessagesSquare,
  ListOrdered, Cpu, Send, AlertTriangle,
  ChevronLeft, ChevronRight, Brain,
} from "lucide-react";
import { theme, cn } from "@/lib/theme";

export interface SidebarSection {
  id: string;
  label: string;
  icon: React.ReactNode;
}

const SECTIONS: SidebarSection[] = [
  { id: "health", label: "Health", icon: <Heart className="w-5 h-5" /> },
  { id: "usage", label: "Uso Global", icon: <BarChart3 className="w-5 h-5" /> },
  { id: "queue", label: "Cola", icon: <ListOrdered className="w-5 h-5" /> },
  { id: "model", label: "Modelo", icon: <Cpu className="w-5 h-5" /> },
  { id: "chat", label: "Chat", icon: <Send className="w-5 h-5" /> },
  { id: "conversations", label: "Conversaciones", icon: <MessagesSquare className="w-5 h-5" /> },
  { id: "errors", label: "Errores", icon: <AlertTriangle className="w-5 h-5" /> },
];

interface SidebarProps {
  active: string;
  onSelect: (id: string) => void;
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ active, onSelect, collapsed, onToggle }: SidebarProps) {
  return (
    <aside
      className={cn(
        theme.colors.card, theme.colors.border,
        "border-r flex flex-col transition-all duration-300",
        collapsed ? "w-16" : "w-56",
      )}
    >
      {/* Header */}
      <div className="flex items-center gap-2 p-4 border-b border-[#30363d]">
        {!collapsed && (
          <a href="/" className="flex items-center gap-2 flex-1 min-w-0">
            <Brain className="w-5 h-5 text-[#58a6ff] shrink-0" />
            <span className="text-sm font-semibold text-[#58a6ff] truncate">Bridge</span>
          </a>
        )}
        <button
          onClick={onToggle}
          className="p-1 rounded hover:bg-[#30363d] text-[#8b949e] hover:text-[#c9d1d9] transition-colors shrink-0 ml-auto"
          aria-label="Toggle sidebar"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Navegación */}
      <nav className="flex-1 py-2 overflow-y-auto">
        {SECTIONS.map((s) => (
          <button
            key={s.id}
            onClick={() => onSelect(s.id)}
            className={cn(
              "w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-all",
              active === s.id
                ? "bg-[#58a6ff]/10 text-[#58a6ff] border-r-2 border-[#58a6ff]"
                : "text-[#8b949e] hover:text-[#c9d1d9] hover:bg-[#30363d]/20",
            )}
          >
            <span className="shrink-0">{s.icon}</span>
            {!collapsed && <span className="truncate">{s.label}</span>}
          </button>
        ))}
      </nav>

      {/* Footer */}
      {!collapsed && (
        <div className="p-3 border-t border-[#30363d]">
          <p className="text-[10px] text-[#484f58] text-center truncate">deco31416.com</p>
        </div>
      )}
    </aside>
  );
}
