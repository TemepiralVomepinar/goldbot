import { StyleSheet, Text, View } from "react-native";
import { colors, spacing } from "@/lib/theme";

export function ComingSoon({ emoji, title, body }: { emoji: string; title: string; body: string }) {
  return (
    <View style={styles.container}>
      <Text style={styles.emoji}>{emoji}</Text>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.body}>{body}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background, padding: spacing.lg, alignItems: "center", justifyContent: "center" },
  emoji: { fontSize: 40, marginBottom: spacing.sm },
  title: { fontSize: 18, fontWeight: "700", color: colors.textPrimary, marginBottom: spacing.xs },
  body: { fontSize: 14, color: colors.textSecondary, textAlign: "center", lineHeight: 20 },
});
