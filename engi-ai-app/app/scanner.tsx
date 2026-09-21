import { useRef, useState } from "react";
import { CameraView, useCameraPermissions } from "expo-camera";
import { router } from "expo-router";
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from "react-native";
import { isSupabaseConfigured, supabase } from "@/lib/supabase";
import { colors, radius, spacing } from "@/lib/theme";

type Choice = { emoji: string; label: string; instruction: string };

const CHOICES: Choice[] = [
  { emoji: "🔵", label: "Spiegazione", instruction: "Spiegami questo esercizio." },
  { emoji: "🟢", label: "Risolvere insieme", instruction: "Aiutami a risolverlo passo dopo passo." },
  { emoji: "🟡", label: "Solo suggerimento", instruction: "Dammi solo un suggerimento per iniziare." },
  { emoji: "🔴", label: "Soluzione completa", instruction: "Mostrami la soluzione completa." },
];

export default function ScannerScreen() {
  const [permission, requestPermission] = useCameraPermissions();
  const cameraRef = useRef<CameraView>(null);
  const [photoBase64, setPhotoBase64] = useState<string | null>(null);
  const [recognizedLabel, setRecognizedLabel] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);

  if (!permission) {
    return <View style={styles.container} />;
  }

  if (!permission.granted) {
    return (
      <View style={styles.permissionContainer}>
        <Text style={styles.permissionText}>ENGI AI ha bisogno della fotocamera per scansionare i tuoi esercizi.</Text>
        <Pressable style={styles.primaryButton} onPress={requestPermission}>
          <Text style={styles.primaryButtonText}>Consenti fotocamera</Text>
        </Pressable>
      </View>
    );
  }

  async function handleCapture() {
    if (!cameraRef.current) return;
    const photo = await cameraRef.current.takePictureAsync({ base64: true, quality: 0.6 });
    if (!photo?.base64) return;
    setPhotoBase64(photo.base64);

    if (!isSupabaseConfigured) {
      setRecognizedLabel("Configura Supabase per il riconoscimento automatico.");
      return;
    }

    setProcessing(true);
    try {
      const { data, error } = await supabase.functions.invoke("ai-tutor", {
        body: { type: "recognize", imageBase64: photo.base64 },
      });
      if (error) throw error;
      setRecognizedLabel(data.label ?? "Esercizio riconosciuto");
    } catch (err) {
      console.warn("[ENGI AI] Riconoscimento fallito:", err);
      setRecognizedLabel("Non sono riuscito a riconoscere l'esercizio, ma puoi comunque continuare in chat.");
    } finally {
      setProcessing(false);
    }
  }

  function handleChoice(choice: Choice) {
    router.replace({
      pathname: "/(tabs)/ai",
      params: {
        subjectName: recognizedLabel ?? undefined,
        topicName: choice.instruction,
      },
    });
  }

  if (photoBase64) {
    return (
      <View style={styles.resultContainer}>
        <Text style={styles.resultTitle}>{processing ? "Analisi in corso…" : recognizedLabel}</Text>
        {processing && <ActivityIndicator color={colors.primary} style={{ marginVertical: spacing.md }} />}

        {!processing && (
          <>
            <Text style={styles.resultSubtitle}>Cosa vuoi fare?</Text>
            <View style={styles.choicesGrid}>
              {CHOICES.map((choice) => (
                <Pressable key={choice.label} style={styles.choiceCard} onPress={() => handleChoice(choice)}>
                  <Text style={styles.choiceEmoji}>{choice.emoji}</Text>
                  <Text style={styles.choiceLabel}>{choice.label}</Text>
                </Pressable>
              ))}
            </View>
            <Pressable
              style={styles.retryButton}
              onPress={() => {
                setPhotoBase64(null);
                setRecognizedLabel(null);
              }}
            >
              <Text style={styles.retryButtonText}>Scatta di nuovo</Text>
            </Pressable>
          </>
        )}
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <CameraView ref={cameraRef} style={StyleSheet.absoluteFill} facing="back" />
      <View style={styles.shutterRow}>
        <Pressable style={styles.shutterButton} onPress={handleCapture}>
          <View style={styles.shutterInner} />
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "black" },
  permissionContainer: { flex: 1, alignItems: "center", justifyContent: "center", padding: spacing.lg, gap: spacing.md, backgroundColor: colors.background },
  permissionText: { fontSize: 15, color: colors.textPrimary, textAlign: "center" },
  primaryButton: { backgroundColor: colors.primary, borderRadius: radius.md, paddingHorizontal: spacing.lg, paddingVertical: spacing.sm },
  primaryButtonText: { color: "#fff", fontWeight: "600" },
  shutterRow: { position: "absolute", bottom: spacing.xl, alignSelf: "center" },
  shutterButton: { width: 72, height: 72, borderRadius: 36, backgroundColor: "rgba(255,255,255,0.3)", alignItems: "center", justifyContent: "center" },
  shutterInner: { width: 58, height: 58, borderRadius: 29, backgroundColor: "white" },
  resultContainer: { flex: 1, backgroundColor: colors.background, padding: spacing.lg },
  resultTitle: { fontSize: 18, fontWeight: "700", color: colors.textPrimary, marginTop: spacing.lg },
  resultSubtitle: { fontSize: 14, color: colors.textSecondary, marginTop: spacing.sm, marginBottom: spacing.md },
  choicesGrid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm },
  choiceCard: {
    width: "47%",
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    padding: spacing.md,
    alignItems: "center",
    gap: spacing.xs,
  },
  choiceEmoji: { fontSize: 24 },
  choiceLabel: { fontSize: 13, fontWeight: "600", color: colors.textPrimary, textAlign: "center" },
  retryButton: { marginTop: spacing.lg, alignItems: "center" },
  retryButtonText: { color: colors.primary, fontWeight: "600" },
});
