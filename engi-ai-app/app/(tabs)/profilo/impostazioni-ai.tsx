import { useState } from "react";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { Card } from "@/components/Card";
import { useAuth } from "@/context/AuthContext";
import { supabase } from "@/lib/supabase";
import { colors, spacing } from "@/lib/theme";
import type { ErrorMode, ExplanationStyle, StudentLevel } from "@/types/database";

const EXPLANATION_STYLES: { key: ExplanationStyle; label: string }[] = [
  { key: "semplice", label: "Semplice" },
  { key: "universitario", label: "Universitario" },
  { key: "tecnico", label: "Tecnico" },
  { key: "dettagliato", label: "Molto dettagliato" },
];

const ERROR_MODES: { key: ErrorMode; label: string }[] = [
  { key: "soluzione", label: "Dammi la soluzione" },
  { key: "suggerimento", label: "Dammi un suggerimento" },
  { key: "ragionare", label: "Fammi ragionare" },
];

const LEVELS: { key: StudentLevel; label: string }[] = [
  { key: "principiante", label: "Principiante" },
  { key: "intermedio", label: "Intermedio" },
  { key: "avanzato", label: "Avanzato" },
];

function OptionGroup<T extends string>({
  title,
  options,
  value,
  onChange,
}: {
  title: string;
  options: { key: T; label: string }[];
  value: T;
  onChange: (key: T) => void;
}) {
  return (
    <Card style={{ gap: spacing.sm }}>
      <Text style={styles.groupTitle}>{title}</Text>
      {options.map((opt) => (
        <Pressable key={opt.key} style={styles.optionRow} onPress={() => onChange(opt.key)}>
          <View style={[styles.radio, value === opt.key && styles.radioActive]} />
          <Text style={styles.optionLabel}>{opt.label}</Text>
        </Pressable>
      ))}
    </Card>
  );
}

export default function ImpostazioniAiScreen() {
  const { profile, session, refreshProfile, supabaseReady } = useAuth();
  const [explanationStyle, setExplanationStyle] = useState<ExplanationStyle>(
    profile?.ai_explanation_style ?? "universitario"
  );
  const [errorMode, setErrorMode] = useState<ErrorMode>(profile?.ai_error_mode ?? "suggerimento");
  const [level, setLevel] = useState<StudentLevel>(profile?.ai_level ?? "intermedio");
  const [saving, setSaving] = useState(false);

  async function persist(update: Partial<{ ai_explanation_style: ExplanationStyle; ai_error_mode: ErrorMode; ai_level: StudentLevel }>) {
    if (!session || !supabaseReady) return;
    setSaving(true);
    await supabase.from("profiles").update(update).eq("id", session.user.id);
    await refreshProfile();
    setSaving(false);
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <OptionGroup
        title="Stile di spiegazione"
        options={EXPLANATION_STYLES}
        value={explanationStyle}
        onChange={(key) => {
          setExplanationStyle(key);
          persist({ ai_explanation_style: key });
        }}
      />
      <OptionGroup
        title="Quando sbaglio"
        options={ERROR_MODES}
        value={errorMode}
        onChange={(key) => {
          setErrorMode(key);
          persist({ ai_error_mode: key });
        }}
      />
      <OptionGroup
        title="Livello"
        options={LEVELS}
        value={level}
        onChange={(key) => {
          setLevel(key);
          persist({ ai_level: key });
        }}
      />
      {saving && <Text style={styles.savingText}>Salvataggio…</Text>}
      {!supabaseReady && (
        <Text style={styles.savingText}>Configura Supabase per salvare le preferenze in modo persistente.</Text>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, gap: spacing.md, paddingBottom: spacing.xl },
  groupTitle: { fontSize: 13, fontWeight: "600", color: colors.textSecondary },
  optionRow: { flexDirection: "row", alignItems: "center", gap: spacing.sm },
  radio: { width: 18, height: 18, borderRadius: 9, borderWidth: 2, borderColor: colors.border },
  radioActive: { borderColor: colors.primary, backgroundColor: colors.primary },
  optionLabel: { fontSize: 14, color: colors.textPrimary },
  savingText: { fontSize: 12, color: colors.textSecondary, textAlign: "center" },
});
