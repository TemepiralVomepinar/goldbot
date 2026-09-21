export const colors = {
  background: "#F5F7FA",
  surface: "#FFFFFF",
  border: "#E2E8F0",
  textPrimary: "#0F172A",
  textSecondary: "#64748B",
  primary: "#4F46E5",
  primarySoft: "#EEF2FF",
  success: "#16A34A",
  successSoft: "#DCFCE7",
  warning: "#CA8A04",
  warningSoft: "#FEF9C3",
  danger: "#DC2626",
  dangerSoft: "#FEE2E2",
  neutral: "#94A3B8",
  neutralSoft: "#F1F5F9",
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
} as const;

export const radius = {
  sm: 8,
  md: 12,
  lg: 20,
  pill: 999,
} as const;

export type ChapterStatus = "non_studiato" | "debole" | "da_ripassare" | "buono";

export const chapterStatusMeta: Record<
  ChapterStatus,
  { emoji: string; label: string; color: string; bg: string }
> = {
  buono: { emoji: "🟢", label: "Buona preparazione", color: colors.success, bg: colors.successSoft },
  da_ripassare: { emoji: "🟡", label: "Da ripassare", color: colors.warning, bg: colors.warningSoft },
  debole: { emoji: "🔴", label: "Debole", color: colors.danger, bg: colors.dangerSoft },
  non_studiato: { emoji: "⚪", label: "Non ancora studiato", color: colors.neutral, bg: colors.neutralSoft },
};
