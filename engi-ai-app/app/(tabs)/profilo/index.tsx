import { router } from "expo-router";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { Card } from "@/components/Card";
import { useAuth } from "@/context/AuthContext";
import { colors, spacing } from "@/lib/theme";

const SETTINGS_ROWS = [
  { emoji: "🤖", label: "Impostazioni AI", href: "/(tabs)/profilo/impostazioni-ai" },
];

export default function ProfiloScreen() {
  const { profile, session, signOut, supabaseReady } = useAuth();

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Card style={styles.header}>
        <Text style={styles.avatar}>👤</Text>
        <Text style={styles.name}>{profile?.full_name ?? session?.user.email ?? "Studente ENGI AI"}</Text>
        <Text style={styles.meta}>{profile?.course ?? "Ingegneria Meccanica"}</Text>
        <Text style={styles.meta}>{profile?.university ?? "Politecnico di Milano"}</Text>
        <Text style={styles.meta}>{profile?.year ? `${profile.year}° anno` : "1° anno"}</Text>
      </Card>

      <Text style={styles.sectionLabel}>Impostazioni</Text>
      {SETTINGS_ROWS.map((row) => (
        <Pressable key={row.href} onPress={() => router.push(row.href as any)}>
          <Card style={styles.row}>
            <Text style={styles.rowEmoji}>{row.emoji}</Text>
            <Text style={styles.rowLabel}>{row.label}</Text>
            <Text style={styles.chevron}>›</Text>
          </Card>
        </Pressable>
      ))}

      {supabaseReady && session && (
        <Pressable style={styles.logoutButton} onPress={signOut}>
          <Text style={styles.logoutText}>Esci</Text>
        </Pressable>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, gap: spacing.sm, paddingBottom: spacing.xl },
  header: { alignItems: "center", gap: 2, paddingVertical: spacing.lg },
  avatar: { fontSize: 40, marginBottom: spacing.xs },
  name: { fontSize: 18, fontWeight: "700", color: colors.textPrimary },
  meta: { fontSize: 13, color: colors.textSecondary },
  sectionLabel: { fontSize: 13, fontWeight: "600", color: colors.textSecondary, marginTop: spacing.md },
  row: { flexDirection: "row", alignItems: "center", gap: spacing.sm },
  rowEmoji: { fontSize: 20 },
  rowLabel: { fontSize: 15, color: colors.textPrimary, flex: 1 },
  chevron: { fontSize: 20, color: colors.neutral },
  logoutButton: { marginTop: spacing.lg, alignItems: "center", padding: spacing.sm },
  logoutText: { color: colors.danger, fontWeight: "600" },
});
