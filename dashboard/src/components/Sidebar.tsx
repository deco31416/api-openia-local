"use client";

import { useEffect } from "react";
import {
  Heart, BarChart3, MessagesSquare,
  ListOrdered, Cpu, Send, AlertTriangle,
  ChevronLeft, ChevronRight, Brain, Menu, X,
} from "lucide-react";
import { theme, cn } from "@/lib/theme";

const SECTIONS = [
  { id: "health", label: "Health", icon: Heart },
  { id: "usage", label: "Uso Global", icon: BarChart3 },
  { id: "queue", label: "Cola", icon: ListOrdered },
  { id: "model", label: "Modelo", icon: Cpu },
  { id: "chat", label: "Chat", icon: Send },
  { id: "conversations", label: "Conversaciones", icon: MessagesSquare },
  { id: "errors", label: "Errores", icon: AlertTriangle },
] as const;

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
  // Cerrar sidebar mobile al seleccionar
  const handleSelect = (id: string) => {
    onSelect(id);
    if (isMobile) onMobileClose();
  };

  const sidebarNav = (
    <nav className="flex-1 py-3 space-y-0.5">
      {SECTIONS.map(({ id, label, icon: Icon }) => {
        const isActive = active === id;
        return (
          <button
            key={id}
            onClick={() => handleSelect(id)}
            title={collapsed && !isMobile ? label : undefined}
            className={cn(
              // Base
              "w-full flex items-center gap-3 px-3 py-2.5 text-sm transition-all duration-200 rounded-lg mx-2",
              // Active
              isActive
                ? "bg-[#58a6ff]/15 text-[#58a6ff] font-medium"
                : "text-[#8b949e] hover:text-[#c9d1d9] hover:bg-[#30363d]/30",
              // Collapsed desktop: centrado
              collapsed && !isMobile && "justify-center px-0 mx-1.5 rounded-xl w-auto",
            )}
          >
            <Icon className={cn(
              "w-5 h-5 shrink-0",
              isActive ? "text-[#58a6ff]" : ""
            )} />
            {(!collapsed || isMobile) && (
              <span className="truncate">{label}</span>
            )}
            {/* Indicador activo: barrita izquierda */}
            {isActive && (!collapsed || isMobile) && (
              <span className="ml-auto w-1 h-4 rounded-full bg-[#58a6ff]" />
            )}
          </button>
        );
      })}
    </nav>
  );

  return (
    <>
      {/* Overlay mobile */}
      {isMobile && mobileOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 transition-opacity"
          onClick={onMobileClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          theme.colors.card,
          "flex flex-col h-full transition-all duration-300 ease-in-out",
          // Desktop
          !isMobile && "border-r border-[#30363d]",
          !isMobile && (collapsed ? "w-[68px]" : "w-[244px]"),
          // Mobile overlay
          isMobile && "fixed inset-y-0 left-0 z-50 w-72 border-r border-[#30363d] shadow-2xl",
          isMobile && (!mobileOpen && "-translate-x-full"),
        )}
      >
        {/* Header */}
        <div className={cn(
          "flex items-center border-b border-[#30363d]",
          collapsed && !isMobile ? "justify-center px-2 py-4" : "px-4 py-3.5"
        )}>
          {(!collapsed || isMobile) && (
            <div className="flex items-center gap-2.5 flex-1 min-w-0">
              <div className="w-7 h-7 rounded-lg bg-[#58a6ff]/20 flex items-center justify-center shrink-0">
                <Brain className="w-4 h-4 text-[#58a6ff]" />
              </div>
              <span className="text-sm font-semibold text-[#c9d1d9] truncate">
                ChatGPT Bridge
              </span>
            </div>
          )}
          {isMobile ? (
            <button onClick={onMobileClose} className="p-1.5 rounded-lg hover:bg-[#30363d] text-[#8b949e]">
              <X className="w-4 h-4" />
            </button>
          ) : (
            <button
              onClick={onToggle}
              className="p-1.5 rounded-lg hover:bg-[#30363d] text-[#8b949e] hover:text-[#c9d1d9] transition-all shrink-0"
            >
              {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
            </button>
          )}
        </div>

        {sidebarNav}

        {/* Footer minimal */}
        <div className={cn(
          "border-t border-[#30363d]",
          collapsed && !isMobile ? "p-2" : "p-3"
        )}>
          {(!collapsed || isMobile) ? (
            <p className="text-[10px] text-[#484f58] text-center truncate">
              deco31416.com
            </p>
          ) : (
            <div className="w-5 h-5 mx-auto rounded-full bg-[#58a6ff]/10 flex items-center justify-center">
              <Brain className="w-3 h-3 text-[#58a6ff]" />
            </div>
          )}
        </div>
      </aside>

      {/* Botón hamburguesa mobile */}
      {isMobile && !mobileOpen && (
        <button
          onClick={() => onMobileClose()}
          className="fixed top-3 left-3 z-30 p-2 rounded-lg bg-[#161b22] border border-[#30363d] text-[#8b949e] shadow-lg"
        >
          <Menu className="w-5 h-5" />
        </button>
      )}
    </>
  );
}


