import { router } from "expo-router";
import { FlatList, Pressable, StyleSheet, Text, View } from "react-native";
import { Card } from "@/components/Card";
import { ProgressBar } from "@/components/ProgressBar";
import { mockSubjects } from "@/data/mock";
import { colors, spacing } from "@/lib/theme";

export default function MaterieScreen() {
  return (
    <FlatList
      style={styles.container}
      contentContainerStyle={styles.content}
      data={mockSubjects}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => (
        <Pressable onPress={() => router.push(`/(tabs)/studio/materie/${item.id}`)}>
          <Card style={styles.card}>
            <View style={styles.headerRow}>
              <Text style={styles.emoji}>{item.icon}</Text>
              <Text style={styles.name}>{item.name}</Text>
            </View>
            <ProgressBar pct={item.progressPct} />
          </Card>
        </Pressable>
      )}
    />
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, gap: spacing.sm, paddingBottom: spacing.xl },
  card: { gap: spacing.sm },
  headerRow: { flexDirection: "row", alignItems: "center", gap: spacing.sm },
  emoji: { fontSize: 22 },
  name: { fontSize: 16, fontWeight: "600", color: colors.textPrimary },
});
