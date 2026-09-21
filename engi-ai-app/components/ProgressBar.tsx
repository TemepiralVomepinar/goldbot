import { StyleSheet, Text, View } from "react-native";
import { colors, radius, spacing } from "@/lib/theme";

export function ProgressBar({ pct, label }: { pct: number; label?: string }) {
  const clamped = Math.max(0, Math.min(100, pct));
  return (
    <View style={styles.wrapper}>
      {label ? <Text style={styles.label}>{label}</Text> : null}
      <View style={styles.track}>
        <View style={[styles.fill, { width: `${clamped}%` }]} />
      </View>
      <Text style={styles.pct}>{clamped}%</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { gap: spacing.xs },
  label: { fontSize: 13, color: colors.textSecondary, fontWeight: "500" },
  track: {
    height: 10,
    borderRadius: radius.pill,
    backgroundColor: colors.neutralSoft,
    overflow: "hidden",
  },
  fill: {
    height: "100%",
    borderRadius: radius.pill,
    backgroundColor: colors.primary,
  },
  pct: { fontSize: 12, color: colors.textSecondary, textAlign: "right" },
});
