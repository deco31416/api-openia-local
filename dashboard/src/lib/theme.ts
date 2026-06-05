// ─── Estilos centralizados (Tailwind + tokens de diseño) ───

export const theme = {
  colors: {
    bg: "bg-[#0d1117]",
    card: "bg-[#161b22]",
    border: "border-[#30363d]",
    text: "text-[#c9d1d9]",
    textMuted: "text-[#8b949e]",
    accent: "text-[#58a6ff]",
    success: "text-[#7ee787]",
    warning: "text-[#d29922]",
    danger: "text-[#f85149]",
    btnPrimary: "bg-[#238636]",
    btnDanger: "bg-[#da3633]",
  },
  layout: {
    page: "min-h-screen p-5 md:p-8",
    header: "mb-6",
    grid: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4",
    card: "rounded-xl border p-5",
    stat: "flex justify-between items-center text-sm py-1",
  },
} as const;

export const cn = (...classes: (string | false | undefined | null)[]): string =>
  classes.filter(Boolean).join(" ");
