import { Stack, router, useLocalSearchParams } from "expo-router";
import { FlatList, Pressable, StyleSheet, Text, View } from "react-native";
import { Card } from "@/components/Card";
import { ChapterStatusBadge } from "@/components/ChapterStatusDot";
import { ProgressBar } from "@/components/ProgressBar";
import { mockSubjects } from "@/data/mock";
import { colors, spacing } from "@/lib/theme";

export default function SubjectDetailScreen() {
  const { subjectId } = useLocalSearchParams<{ subjectId: string }>();
  const subject = mockSubjects.find((s) => s.id === subjectId);

  if (!subject) {
    return (
      <View style={styles.container}>
        <Text>Materia non trovata.</Text>
      </View>
    );
  }

  return (
    <>
      <Stack.Screen options={{ title: subject.name }} />
      <FlatList
        style={styles.container}
        contentContainerStyle={styles.content}
        ListHeaderComponent={
          <Card style={styles.progressCard}>
            <Text style={styles.progressLabel}>📊 Progresso</Text>
            <ProgressBar pct={subject.progressPct} />
          </Card>
        }
        data={subject.chapters}
        keyExtractor={(item) => item.id}
        renderItem={({ item, index }) => (
          <Pressable
            disabled={item.topics.length === 0}
            onPress={() => router.push(`/(tabs)/studio/materie/${subject.id}/${item.topics[0]?.id}`)}
          >
            <Card style={styles.chapterCard}>
              <Text style={styles.chapterTitle}>
                {index + 1}. {item.title}
              </Text>
              <ChapterStatusBadge status={item.status} />
            </Card>
          </Pressable>
        )}
      />
    </>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, gap: spacing.sm, paddingBottom: spacing.xl },
  progressCard: { marginBottom: spacing.sm },
  progressLabel: { fontSize: 13, fontWeight: "600", color: colors.textSecondary, marginBottom: spacing.xs },
  chapterCard: { gap: spacing.xs },
  chapterTitle: { fontSize: 15, fontWeight: "600", color: colors.textPrimary },
});
