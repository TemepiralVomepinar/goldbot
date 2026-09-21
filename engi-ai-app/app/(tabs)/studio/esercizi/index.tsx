import { router } from "expo-router";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { Card } from "@/components/Card";
import { colors, spacing } from "@/lib/theme";

const DIFFICULTIES = ["⭐ Facile", "⭐⭐ Medio", "⭐⭐⭐ Difficile", "⭐⭐⭐⭐ Esame"];

const MODES = [
  { emoji: "🎲", title: "Allenamento", subtitle: "10 esercizi casuali" },
  { emoji: "🔎", title: "Argomento specifico", subtitle: "Scegli materia e argomento" },
  { emoji: "❌", title: "Errori", subtitle: "Solo esercizi sbagliati in precedenza" },
  { emoji: "🎓", title: "Esame", subtitle: "Simulazione completa", href: "/(tabs)/studio/esami" },
];

export default function EserciziScreen() {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.sectionLabel}>Difficoltà</Text>
      <View style={styles.chipsRow}>
        {DIFFICULTIES.map((d) => (
          <View key={d} style={styles.chip}>
            <Text style={styles.chipText}>{d}</Text>
          </View>
        ))}
      </View>

      <Text style={styles.sectionLabel}>Modalità</Text>
      {MODES.map((mode) => (
        <Pressable key={mode.title} onPress={() => mode.href && router.push(mode.href as any)}>
          <Card style={styles.modeCard}>
            <Text style={styles.modeEmoji}>{mode.emoji}</Text>
            <View style={{ flex: 1 }}>
              <Text style={styles.modeTitle}>{mode.title}</Text>
              <Text style={styles.modeSubtitle}>{mode.subtitle}</Text>
            </View>
          </Card>
        </Pressable>
      ))}

      <Pressable style={styles.scanButton} onPress={() => router.push("/scanner")}>
        <Text style={styles.scanButtonText}>📷 Scansiona esercizio</Text>
      </Pressable>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, gap: spacing.sm, paddingBottom: spacing.xl },
  sectionLabel: { fontSize: 13, fontWeight: "600", color: colors.textSecondary, marginTop: spacing.sm },
  chipsRow: { flexDirection: "row", flexWrap: "wrap", gap: spacing.xs },
  chip: { backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, borderRadius: 999, paddingHorizontal: spacing.sm, paddingVertical: 6 },
  chipText: { fontSize: 12, color: colors.textPrimary },
  modeCard: { flexDirection: "row", alignItems: "center", gap: spacing.md },
  modeEmoji: { fontSize: 24 },
  modeTitle: { fontSize: 15, fontWeight: "600", color: colors.textPrimary },
  modeSubtitle: { fontSize: 13, color: colors.textSecondary },
  scanButton: {
    marginTop: spacing.md,
    backgroundColor: colors.primary,
    borderRadius: 999,
    paddingVertical: spacing.md,
    alignItems: "center",
  },
  scanButtonText: { color: "#fff", fontSize: 16, fontWeight: "700" },
});
