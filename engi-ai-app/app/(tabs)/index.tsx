import { router } from "expo-router";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { Card } from "@/components/Card";
import { useAuth } from "@/context/AuthContext";
import { mockSubjects, nextExam, todayGoal } from "@/data/mock";
import { colors, spacing } from "@/lib/theme";

function daysUntil(dateStr: string) {
  const diff = new Date(dateStr).getTime() - Date.now();
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
}

export default function HomeScreen() {
  const { profile } = useAuth();
  const continueSubject = mockSubjects[0];
  const firstName = profile?.full_name?.split(" ")[0] ?? "studente";

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View>
        <Text style={styles.greeting}>👋 Ciao, {firstName}</Text>
        <Text style={styles.meta}>
          {profile?.course ?? "Ingegneria Meccanica"} · {profile?.year ? `${profile.year}° anno` : "1° anno"}
        </Text>
        <Text style={styles.meta}>{profile?.university ?? "Politecnico di Milano"}</Text>
      </View>

      <Pressable
        onPress={() => router.push(`/(tabs)/studio/materie/${continueSubject.id}`)}
      >
        <Card style={styles.continueCard}>
          <Text style={styles.sectionLabel}>Continua a studiare</Text>
          <Text style={styles.continueTitle}>
            {continueSubject.icon} {continueSubject.name}
          </Text>
          <Text style={styles.continueTopic}>Integrali indefiniti</Text>
          <Text style={styles.continueCta}>Continua →</Text>
        </Card>
      </Pressable>

      <Card>
        <Text style={styles.sectionLabel}>Oggi</Text>
        <View style={styles.todayRow}>
          <Text style={styles.todayItem}>📚 {todayGoal.hoursTarget}h da studiare</Text>
          <Text style={styles.todayItem}>📝 {todayGoal.exercisesTarget} esercizi</Text>
        </View>
        <Text style={styles.todayItem}>🎯 Obiettivo giornaliero: {todayGoal.goalPct}%</Text>
      </Card>

      <Card>
        <Text style={styles.sectionLabel}>Prossimo esame</Text>
        <Text style={styles.examSubject}>{nextExam.subjectName}</Text>
        <Text style={styles.examDate}>
          {new Date(nextExam.date).toLocaleDateString("it-IT", { day: "numeric", month: "long", year: "numeric" })}
        </Text>
        <Text style={styles.examCountdown}>⏱️ {daysUntil(nextExam.date)} giorni</Text>
      </Card>

      <Pressable style={styles.aiButton} onPress={() => router.push("/(tabs)/ai")}>
        <Text style={styles.aiButtonText}>🤖 Chiedi a ENGI</Text>
      </Pressable>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, gap: spacing.md, paddingBottom: spacing.xl },
  greeting: { fontSize: 24, fontWeight: "700", color: colors.textPrimary },
  meta: { fontSize: 14, color: colors.textSecondary, marginTop: 2 },
  sectionLabel: { fontSize: 13, fontWeight: "600", color: colors.textSecondary, marginBottom: spacing.xs },
  continueCard: { backgroundColor: colors.primarySoft, borderColor: colors.primarySoft },
  continueTitle: { fontSize: 18, fontWeight: "700", color: colors.textPrimary },
  continueTopic: { fontSize: 14, color: colors.textSecondary, marginTop: 2 },
  continueCta: { fontSize: 14, fontWeight: "600", color: colors.primary, marginTop: spacing.sm },
  todayRow: { flexDirection: "row", justifyContent: "space-between", marginBottom: spacing.xs },
  todayItem: { fontSize: 14, color: colors.textPrimary },
  examSubject: { fontSize: 16, fontWeight: "600", color: colors.textPrimary },
  examDate: { fontSize: 14, color: colors.textSecondary, marginTop: 2 },
  examCountdown: { fontSize: 14, fontWeight: "600", color: colors.danger, marginTop: spacing.xs },
  aiButton: {
    backgroundColor: colors.primary,
    borderRadius: 999,
    paddingVertical: spacing.md,
    alignItems: "center",
  },
  aiButtonText: { color: "#fff", fontSize: 16, fontWeight: "700" },
});
