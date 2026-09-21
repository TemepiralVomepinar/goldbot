import { useState } from "react";
import { Stack, router, useLocalSearchParams } from "expo-router";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { Card } from "@/components/Card";
import { mockSubjects } from "@/data/mock";
import { colors, spacing } from "@/lib/theme";

const TABS = [
  { key: "teoria", label: "📖 Teoria" },
  { key: "formule", label: "📐 Formule" },
  { key: "esempi", label: "💡 Esempi" },
  { key: "esercizi", label: "✏️ Esercizi" },
  { key: "tutor", label: "🤖 Tutor AI" },
] as const;

type TabKey = (typeof TABS)[number]["key"];

export default function TopicScreen() {
  const { subjectId, topicId } = useLocalSearchParams<{ subjectId: string; topicId: string }>();
  const [tab, setTab] = useState<TabKey>("teoria");

  const subject = mockSubjects.find((s) => s.id === subjectId);
  const topic = subject?.chapters.flatMap((c) => c.topics).find((t) => t.id === topicId);

  if (!subject || !topic) {
    return (
      <View style={styles.container}>
        <Text>Argomento non trovato.</Text>
      </View>
    );
  }

  return (
    <>
      <Stack.Screen options={{ title: topic.title }} />
      <View style={styles.tabBar}>
        {TABS.map((t) => (
          <Pressable key={t.key} onPress={() => setTab(t.key)} style={[styles.tabItem, tab === t.key && styles.tabItemActive]}>
            <Text style={[styles.tabLabel, tab === t.key && styles.tabLabelActive]}>{t.label}</Text>
          </Pressable>
        ))}
      </View>

      <ScrollView style={styles.container} contentContainerStyle={styles.content}>
        {tab === "teoria" && (
          <Card>
            <Text style={styles.body}>{topic.theory}</Text>
          </Card>
        )}

        {tab === "formule" && (
          <Card style={{ gap: spacing.sm }}>
            {topic.formulas.map((f) => (
              <Text key={f} style={styles.formula}>
                {f}
              </Text>
            ))}
          </Card>
        )}

        {tab === "esempi" && (
          <Card style={{ gap: spacing.sm }}>
            {topic.examples.map((e) => (
              <Text key={e} style={styles.body}>
                {e}
              </Text>
            ))}
          </Card>
        )}

        {tab === "esercizi" && (
          <Card>
            <Text style={styles.body}>
              Gli esercizi su questo argomento sono nella sezione Esercizi, filtrabili per capitolo.
            </Text>
            <Pressable style={styles.linkButton} onPress={() => router.push("/(tabs)/studio/esercizi")}>
              <Text style={styles.linkButtonText}>Vai agli esercizi →</Text>
            </Pressable>
          </Card>
        )}

        {tab === "tutor" && (
          <Card>
            <Text style={styles.body}>
              Chiedi al Tutor AI di spiegarti "{topic.title}" — l'AI userà il contesto di questo argomento.
            </Text>
            <Pressable
              style={styles.linkButton}
              onPress={() =>
                router.push({
                  pathname: "/(tabs)/ai",
                  params: { subjectName: subject.name, topicName: topic.title },
                })
              }
            >
              <Text style={styles.linkButtonText}>Apri il Tutor AI →</Text>
            </Pressable>
          </Card>
        )}
      </ScrollView>
    </>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, paddingBottom: spacing.xl },
  tabBar: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.xs,
    padding: spacing.sm,
    backgroundColor: colors.background,
  },
  tabItem: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 6,
    borderRadius: 999,
    backgroundColor: colors.neutralSoft,
  },
  tabItemActive: { backgroundColor: colors.primary },
  tabLabel: { fontSize: 13, color: colors.textSecondary, fontWeight: "600" },
  tabLabelActive: { color: "#fff" },
  body: { fontSize: 15, color: colors.textPrimary, lineHeight: 22 },
  formula: { fontSize: 16, fontWeight: "600", color: colors.primary },
  linkButton: { marginTop: spacing.md },
  linkButtonText: { color: colors.primary, fontWeight: "600" },
});
