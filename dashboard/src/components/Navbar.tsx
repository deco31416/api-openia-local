"use client";

import { Brain, Circle } from "lucide-react";
import { theme, cn } from "@/lib/theme";

interface NavbarProps {
  status: "healthy" | "degraded" | "unhealthy";
  version: string;
  uptime: number;
}

export function Navbar({ status, version, uptime }: NavbarProps) {
  const statusColor = status === "healthy" ? "text-green-400" : status === "degraded" ? "text-yellow-400" : "text-red-400";

  return (
    <nav className={cn(theme.colors.card, theme.colors.border, "border-b px-5 py-3")}>
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Brain className="w-6 h-6 text-blue-400" />
          <span className={cn(theme.colors.accent, "font-bold text-lg")}>ChatGPT Web Bridge</span>
          <span className={cn(theme.colors.textMuted, "text-xs hidden sm:inline")}>deco31416.com</span>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <span className={cn(statusColor, "hidden md:inline-flex items-center gap-1")}>
            <Circle className="w-2 h-2 fill-current" />
            {status}
          </span>
          <span className={cn(theme.colors.textMuted, "hidden md:inline")}>
            ⏱ {Math.floor(uptime / 60)}m
          </span>
          <span className={cn(theme.colors.textMuted, "text-xs")}>v{version}</span>
        </div>
      </div>
    </nav>
  );
}
