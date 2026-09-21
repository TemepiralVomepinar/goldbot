import { ScrollView, StyleSheet, Text, View } from "react-native";
import { Card } from "@/components/Card";
import { ProgressBar } from "@/components/ProgressBar";
import { mockSubjects, overallProgressPct, weakAreas } from "@/data/mock";
import { colors, spacing } from "@/lib/theme";

export default function ProgressiScreen() {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Card>
        <Text style={styles.sectionLabel}>Preparazione semestre</Text>
        <ProgressBar pct={overallProgressPct} />
      </Card>

      <Card>
        <Text style={styles.sectionLabel}>Materie</Text>
        <View style={{ gap: spacing.md }}>
          {mockSubjects.map((subject) => (
            <View key={subject.id}>
              <View style={styles.subjectRow}>
                <Text style={styles.subjectName}>
                  {subject.icon} {subject.name}
                </Text>
                <Text style={styles.subjectPct}>{subject.progressPct}%</Text>
              </View>
              <ProgressBar pct={subject.progressPct} />
            </View>
          ))}
        </View>
      </Card>

      <Card>
        <Text style={styles.sectionLabel}>⚠️ Punti deboli</Text>
        {weakAreas.map((area) => (
          <Text key={area} style={styles.weakArea}>
            • {area}
          </Text>
        ))}
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, gap: spacing.md, paddingBottom: spacing.xl },
  sectionLabel: { fontSize: 13, fontWeight: "600", color: colors.textSecondary, marginBottom: spacing.sm },
  subjectRow: { flexDirection: "row", justifyContent: "space-between", marginBottom: 4 },
  subjectName: { fontSize: 14, color: colors.textPrimary, fontWeight: "500" },
  subjectPct: { fontSize: 14, color: colors.textSecondary },
  weakArea: { fontSize: 14, color: colors.danger, marginTop: 4 },
});
