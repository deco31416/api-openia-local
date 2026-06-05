"use client";

import { useState, useEffect } from "react";
import {
  Heart, BarChart3, MessagesSquare,
  ListOrdered, Cpu, Send, AlertTriangle,
  ChevronLeft, ChevronRight, Brain, Menu, X,
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
  mobileOpen: boolean;
  onMobileClose: () => void;
  isMobile: boolean;
}

export function Sidebar({ active, onSelect, collapsed, onToggle, mobileOpen, onMobileClose, isMobile }: SidebarProps) {
  const sidebarContent = (
    <aside
      className={cn(
        theme.colors.card, theme.colors.border,
        "flex flex-col h-full transition-all duration-300",
        // Desktop
        !isMobile && "border-r",
        !isMobile && (collapsed ? "w-16" : "w-60"),
        // Mobile: overlay fijo a la izquierda
        isMobile && "fixed inset-y-0 left-0 z-50 w-64 border-r shadow-2xl",
        isMobile && (!mobileOpen && "-translate-x-full"),
      )}
    >
      {/* Header */}
      <div className="flex items-center gap-2 p-4 border-b border-[#30363d]">
        <button
          onClick={() => { onSelect("health"); onMobileClose(); }}
          className="flex items-center gap-2 flex-1 min-w-0 hover:opacity-80"
        >
          <Brain className="w-5 h-5 text-[#58a6ff] shrink-0" />
          {(!collapsed || isMobile) && (
            <span className="text-sm font-semibold text-[#58a6ff] truncate">Bridge</span>
          )}
        </button>
        {isMobile ? (
          <button onClick={onMobileClose} className="p-1 rounded hover:bg-[#30363d] text-[#8b949e]">
            <X className="w-4 h-4" />
          </button>
        ) : (
          <button
            onClick={onToggle}
            className="p-1 rounded hover:bg-[#30363d] text-[#8b949e] hover:text-[#c9d1d9] transition-colors shrink-0"
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        )}
      </div>

      {/* Navegación */}
      <nav className="flex-1 py-2 overflow-y-auto">
        {SECTIONS.map((s) => (
          <button
            key={s.id}
            onClick={() => { onSelect(s.id); onMobileClose(); }}
            className={cn(
              "w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-all",
              active === s.id
                ? "bg-[#58a6ff]/10 text-[#58a6ff] border-r-2 border-[#58a6ff]"
                : "text-[#8b949e] hover:text-[#c9d1d9] hover:bg-[#30363d]/20",
            )}
          >
            <span className="shrink-0">{s.icon}</span>
            {(!collapsed || isMobile) && <span className="truncate">{s.label}</span>}
          </button>
        ))}
      </nav>

      {/* Footer */}
      {(!collapsed || isMobile) && (
        <div className="p-3 border-t border-[#30363d]">
          <p className="text-[10px] text-[#484f58] text-center truncate">deco31416.com</p>
        </div>
      )}
    </aside>
  );

  return (
    <>
      {/* Mobile: hamburger + overlay */}
      {isMobile && (
        <>
          <button
            onClick={() => onMobileClose()}
            className={cn(
              "fixed inset-0 bg-black/50 z-40 transition-opacity",
              mobileOpen ? "opacity-100" : "opacity-0 pointer-events-none",
            )}
          />
          <button
            onClick={() => onMobileClose()}
            className="fixed top-3 left-3 z-30 p-2 rounded-lg bg-[#161b22] border border-[#30363d] text-[#8b949e]"
          >
            <Menu className="w-5 h-5" />
          </button>
        </>
      )}

      {sidebarContent}
    </>
  );
}

