import { router } from "expo-router";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { Card } from "@/components/Card";
import { colors, spacing } from "@/lib/theme";

const items: { emoji: string; title: string; subtitle: string; href: string; badge?: string }[] = [
  { emoji: "📚", title: "Materie", subtitle: "Insegnamenti, capitoli e argomenti", href: "/(tabs)/studio/materie" },
  { emoji: "📝", title: "Esercizi", subtitle: "Allenamento, errori, esame", href: "/(tabs)/studio/esercizi" },
  { emoji: "📂", title: "Materiali", subtitle: "PDF, appunti e slide caricate", href: "/(tabs)/studio/materiali" },
  { emoji: "🎯", title: "Piano di studio", subtitle: "Il tuo piano generato dall'AI", href: "/(tabs)/studio/piano", badge: "V2" },
  { emoji: "🧮", title: "Strumenti", subtitle: "Calcolatrice, grafici, unità", href: "/(tabs)/studio/strumenti", badge: "V3" },
  { emoji: "🎓", title: "Esami", subtitle: "Simulazioni cronometrate", href: "/(tabs)/studio/esami", badge: "V2" },
];

export default function StudioHub() {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {items.map((item) => (
        <Pressable key={item.href} onPress={() => router.push(item.href as any)}>
          <Card style={styles.row}>
            <Text style={styles.emoji}>{item.emoji}</Text>
            <View style={styles.textCol}>
              <View style={styles.titleRow}>
                <Text style={styles.title}>{item.title}</Text>
                {item.badge ? (
                  <View style={styles.badge}>
                    <Text style={styles.badgeText}>{item.badge}</Text>
                  </View>
                ) : null}
              </View>
              <Text style={styles.subtitle}>{item.subtitle}</Text>
            </View>
            <Text style={styles.chevron}>›</Text>
          </Card>
        </Pressable>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, gap: spacing.sm, paddingBottom: spacing.xl },
  row: { flexDirection: "row", alignItems: "center", gap: spacing.md },
  emoji: { fontSize: 26 },
  textCol: { flex: 1 },
  titleRow: { flexDirection: "row", alignItems: "center", gap: spacing.xs },
  title: { fontSize: 16, fontWeight: "600", color: colors.textPrimary },
  subtitle: { fontSize: 13, color: colors.textSecondary, marginTop: 2 },
  chevron: { fontSize: 22, color: colors.neutral },
  badge: { backgroundColor: colors.neutralSoft, borderRadius: 6, paddingHorizontal: 6, paddingVertical: 1 },
  badgeText: { fontSize: 10, fontWeight: "700", color: colors.textSecondary },
});
