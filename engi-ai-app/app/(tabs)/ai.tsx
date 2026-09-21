import { useState } from "react";
import { useLocalSearchParams } from "expo-router";
import {
  ActivityIndicator,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  View,
} from "react-native";
import { useAuth } from "@/context/AuthContext";
import { isSupabaseConfigured, supabase } from "@/lib/supabase";
import { colors, radius, spacing } from "@/lib/theme";
import type { AiTutorMode } from "@/types/database";

const MODES: { key: AiTutorMode; label: string; hint: string }[] = [
  { key: "spiegami", label: "Spiegami", hint: "Spiegami le derivate." },
  { key: "esercitati", label: "Fammi esercitare", hint: "Dammi un esercizio sulle derivate." },
  { key: "aiutami", label: "Aiutami", hint: "Non riesco a risolvere questo esercizio." },
  { key: "controlla", label: "Controlla", hint: "Ho fatto questo procedimento. Dove sbaglio?" },
  { key: "interrogami", label: "Interrogami", hint: "Fammi domande sulla teoria." },
];

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export default function AiTutorScreen() {
  const { subjectName, topicName } = useLocalSearchParams<{ subjectName?: string; topicName?: string }>();
  const { profile } = useAuth();
  const [mode, setMode] = useState<AiTutorMode>("spiegami");
  const [noSolution, setNoSolution] = useState(true);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  async function handleSend() {
    const text = input.trim();
    if (!text || sending) return;

    const userMessage: ChatMessage = { id: `${Date.now()}-user`, role: "user", content: text };
    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);
    setInput("");
    setSending(true);

    try {
      const { data, error } = await supabase.functions.invoke("ai-tutor", {
        body: {
          mode,
          noSolution,
          subjectName: subjectName ?? null,
          topicName: topicName ?? null,
          explanationStyle: profile?.ai_explanation_style ?? "universitario",
          level: profile?.ai_level ?? "intermedio",
          messages: nextMessages.map(({ role, content }) => ({ role, content })),
        },
      });
      if (error) throw error;

      setMessages((prev) => [...prev, { id: `${Date.now()}-assistant`, role: "assistant", content: data.reply }]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: `${Date.now()}-error`,
          role: "assistant",
          content: "⚠️ Non sono riuscito a rispondere. Riprova tra poco.",
        },
      ]);
      console.warn("[ENGI AI] Errore ai-tutor:", err?.message ?? err);
    } finally {
      setSending(false);
    }
  }

  const currentHint = MODES.find((m) => m.key === mode)?.hint ?? "";

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
      keyboardVerticalOffset={90}
    >
      {(subjectName || topicName) && (
        <View style={styles.contextBanner}>
          <Text style={styles.contextText}>
            📎 Contesto: {subjectName} {topicName ? `· ${topicName}` : ""}
          </Text>
        </View>
      )}

      <View style={styles.modeRow}>
        {MODES.map((m) => (
          <Pressable key={m.key} onPress={() => setMode(m.key)} style={[styles.modeChip, mode === m.key && styles.modeChipActive]}>
            <Text style={[styles.modeChipText, mode === m.key && styles.modeChipTextActive]}>{m.label}</Text>
          </Pressable>
        ))}
      </View>

      <View style={styles.noSolutionRow}>
        <Text style={styles.noSolutionLabel}>🚫 Non darmi la soluzione — solo piccoli suggerimenti</Text>
        <Switch value={noSolution} onValueChange={setNoSolution} />
      </View>

      {!isSupabaseConfigured && (
        <View style={styles.warningBanner}>
          <Text style={styles.warningText}>
            Configura EXPO_PUBLIC_SUPABASE_URL/ANON_KEY e la funzione ai-tutor per attivare il Tutor AI.
          </Text>
        </View>
      )}

      <FlatList
        style={styles.list}
        contentContainerStyle={styles.listContent}
        data={messages}
        keyExtractor={(item) => item.id}
        ListEmptyComponent={<Text style={styles.emptyHint}>{`Prova: "${currentHint}"`}</Text>}
        renderItem={({ item }) => (
          <View style={[styles.bubble, item.role === "user" ? styles.bubbleUser : styles.bubbleAssistant]}>
            <Text style={item.role === "user" ? styles.bubbleTextUser : styles.bubbleTextAssistant}>
              {item.content}
            </Text>
          </View>
        )}
      />

      <View style={styles.inputRow}>
        <TextInput
          style={styles.input}
          placeholder="Scrivi al tuo tutor…"
          value={input}
          onChangeText={setInput}
          multiline
          editable={isSupabaseConfigured}
        />
        <Pressable style={styles.sendButton} onPress={handleSend} disabled={sending || !isSupabaseConfigured}>
          {sending ? <ActivityIndicator color="#fff" /> : <Text style={styles.sendButtonText}>➤</Text>}
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  contextBanner: { backgroundColor: colors.primarySoft, padding: spacing.sm, paddingHorizontal: spacing.md },
  contextText: { fontSize: 12, color: colors.primary, fontWeight: "600" },
  modeRow: { flexDirection: "row", flexWrap: "wrap", gap: spacing.xs, padding: spacing.md, paddingBottom: spacing.xs },
  modeChip: { paddingHorizontal: spacing.sm, paddingVertical: 6, borderRadius: 999, backgroundColor: colors.neutralSoft },
  modeChipActive: { backgroundColor: colors.primary },
  modeChipText: { fontSize: 12, fontWeight: "600", color: colors.textSecondary },
  modeChipTextActive: { color: "#fff" },
  noSolutionRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: spacing.md,
    paddingBottom: spacing.sm,
  },
  noSolutionLabel: { fontSize: 12, color: colors.textSecondary, flex: 1, marginRight: spacing.sm },
  warningBanner: { backgroundColor: colors.warningSoft, padding: spacing.sm, marginHorizontal: spacing.md, borderRadius: radius.sm, marginBottom: spacing.sm },
  warningText: { fontSize: 12, color: colors.warning },
  list: { flex: 1 },
  listContent: { padding: spacing.md, gap: spacing.sm, flexGrow: 1 },
  emptyHint: { color: colors.textSecondary, textAlign: "center", marginTop: spacing.xl, fontStyle: "italic" },
  bubble: { maxWidth: "85%", padding: spacing.sm, borderRadius: radius.md },
  bubbleUser: { backgroundColor: colors.primary, alignSelf: "flex-end" },
  bubbleAssistant: { backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, alignSelf: "flex-start" },
  bubbleTextUser: { color: "#fff", fontSize: 14 },
  bubbleTextAssistant: { color: colors.textPrimary, fontSize: 14 },
  inputRow: { flexDirection: "row", padding: spacing.md, gap: spacing.sm, alignItems: "flex-end" },
  input: {
    flex: 1,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    maxHeight: 100,
  },
  sendButton: {
    backgroundColor: colors.primary,
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: "center",
    justifyContent: "center",
  },
  sendButtonText: { color: "#fff", fontSize: 18, fontWeight: "700" },
});
