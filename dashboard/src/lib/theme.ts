// ─── Estilos centralizados — ÚNICA fuente de verdad ───

export const color = {
  // Fondo principal (GitHub dark)
  bg:         "#0d1117",
  // Tarjetas / paneles
  card:       "#161b22",
  // Bordes
  border:     "#30363d",
  // Texto principal
  text:       "#c9d1d9",
  // Texto secundario
  muted:      "#8b949e",
  // Acento / links
  accent:     "#58a6ff",
  // Éxito / verde
  success:    "#7ee787",
  // Advertencia / amarillo
  warning:    "#d29922",
  // Error / rojo
  danger:     "#f85149",
  // Botón primario (verde)
  primary:    "#238636",
  // Botón peligro (rojo)
  destructive:"#da3633",
  // Input / select
  input:      "#0d1117",
  placeholder:"#484f58",
} as const;

export const theme = {
  colors: {
    bg:         `bg-[#${color.bg.slice(1)}]`,
    card:       `bg-[#${color.card.slice(1)}]`,
    border:     `border-[#${color.border.slice(1)}]`,
    text:       `text-[#${color.text.slice(1)}]`,
    textMuted:  `text-[#${color.muted.slice(1)}]`,
    accent:     `text-[#${color.accent.slice(1)}]`,
    success:    `text-[#${color.success.slice(1)}]`,
    warning:    `text-[#${color.warning.slice(1)}]`,
    danger:     `text-[#${color.danger.slice(1)}]`,
    primary:    `bg-[#${color.primary.slice(1)}]`,
    destructive:`bg-[#${color.destructive.slice(1)}]`,
  },
  // Variantes compuestas para componentes
  input: `bg-[#${color.input.slice(1)}] border-[#${color.border.slice(1)}] text-[#${color.text.slice(1)}] placeholder-[#${color.placeholder.slice(1)}]`,
  inputFocus: "focus:outline-none focus:border-[#58a6ff]",
  selectBase: "bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-1.5 text-sm text-[#c9d1d9]",
  textarea: "bg-[#0d1117] border border-[#30363d] rounded-lg px-3 py-2 text-sm text-[#c9d1d9] placeholder-[#484f58] resize-none focus:outline-none focus:border-[#58a6ff]",
  badge: {
    ok:     "bg-[#238636]/20 text-[#7ee787]",
    warn:   "bg-[#d29922]/20 text-[#d29922]",
    error:  "bg-[#da3633]/20 text-[#f85149]",
  },
  btn: {
    primary:   "bg-[#238636] text-white hover:bg-[#2ea043]",
    disabled:  "bg-[#30363d] text-[#484f58] cursor-not-allowed",
  },
  modelActive:   "bg-[#58a6ff]/20 text-[#58a6ff] border border-[#58a6ff]/30 font-semibold",
  modelInactive: "text-[#8b949e] hover:text-[#c9d1d9] hover:bg-[#30363d]/30",
  divider: "border-t border-[#30363d]",
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

