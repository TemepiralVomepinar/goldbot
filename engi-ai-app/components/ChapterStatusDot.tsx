import { StyleSheet, Text, View } from "react-native";
import { chapterStatusMeta, spacing, type ChapterStatus } from "@/lib/theme";

export function ChapterStatusBadge({ status }: { status: ChapterStatus }) {
  const meta = chapterStatusMeta[status];
  return (
    <View style={[styles.badge, { backgroundColor: meta.bg }]}>
      <Text style={styles.emoji}>{meta.emoji}</Text>
      <Text style={[styles.label, { color: meta.color }]}>{meta.label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: 999,
    alignSelf: "flex-start",
  },
  emoji: { fontSize: 12 },
  label: { fontSize: 12, fontWeight: "600" },
});
