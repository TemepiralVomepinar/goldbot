import { useCallback, useEffect, useState } from "react";
import * as DocumentPicker from "expo-document-picker";
import { ActivityIndicator, FlatList, Pressable, StyleSheet, Text, View } from "react-native";
import { Card } from "@/components/Card";
import { useAuth } from "@/context/AuthContext";
import { isSupabaseConfigured, supabase } from "@/lib/supabase";
import { colors, spacing } from "@/lib/theme";
import type { Material } from "@/types/database";

export default function MaterialiScreen() {
  const { session, supabaseReady } = useAuth();
  const [materials, setMaterials] = useState<Material[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  const loadMaterials = useCallback(async () => {
    if (!session) return;
    const { data } = await supabase
      .from("materials")
      .select("*")
      .order("uploaded_at", { ascending: false });
    setMaterials((data as Material[]) ?? []);
    setLoading(false);
  }, [session]);

  useEffect(() => {
    if (supabaseReady && session) {
      loadMaterials();
    } else {
      setLoading(false);
    }
  }, [supabaseReady, session, loadMaterials]);

  async function handleUpload() {
    if (!session) return;
    const result = await DocumentPicker.getDocumentAsync({
      type: ["application/pdf", "image/*", "application/msword", "application/vnd.openxmlformats-officedocument.*"],
      copyToCacheDirectory: true,
    });
    if (result.canceled || !result.assets?.[0]) return;

    const file = result.assets[0];
    setUploading(true);
    try {
      const response = await fetch(file.uri);
      const blob = await response.blob();
      const storagePath = `${session.user.id}/${Date.now()}-${file.name}`;

      const { error: uploadError } = await supabase.storage.from("materials").upload(storagePath, blob, {
        contentType: file.mimeType ?? "application/octet-stream",
      });
      if (uploadError) throw uploadError;

      await supabase.from("materials").insert({
        user_id: session.user.id,
        file_name: file.name,
        storage_path: storagePath,
        mime_type: file.mimeType ?? null,
      });

      await loadMaterials();
    } catch (err) {
      console.warn("[ENGI AI] Upload materiale fallito:", err);
    } finally {
      setUploading(false);
    }
  }

  if (!supabaseReady) {
    return (
      <View style={styles.emptyState}>
        <Text style={styles.emptyTitle}>Configura Supabase</Text>
        <Text style={styles.emptyBody}>
          Imposta EXPO_PUBLIC_SUPABASE_URL e EXPO_PUBLIC_SUPABASE_ANON_KEY (vedi .env.example) per caricare e
          consultare i tuoi materiali.
        </Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Pressable style={styles.uploadButton} onPress={handleUpload} disabled={uploading}>
        {uploading ? <ActivityIndicator color="#fff" /> : <Text style={styles.uploadButtonText}>📁 Carica materiale</Text>}
      </Pressable>

      {loading ? (
        <ActivityIndicator style={{ marginTop: spacing.lg }} color={colors.primary} />
      ) : (
        <FlatList
          contentContainerStyle={styles.list}
          data={materials}
          keyExtractor={(item) => item.id}
          ListEmptyComponent={
            <Text style={styles.emptyBody}>Non hai ancora caricato materiali. Inizia con le slide di un corso.</Text>
          }
          renderItem={({ item }) => (
            <Card style={styles.materialRow}>
              <Text style={styles.materialEmoji}>📄</Text>
              <View style={{ flex: 1 }}>
                <Text style={styles.materialName}>{item.file_name}</Text>
                <Text style={styles.materialMeta}>
                  {new Date(item.uploaded_at).toLocaleDateString("it-IT")}
                </Text>
              </View>
            </Card>
          )}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background, padding: spacing.md },
  uploadButton: {
    backgroundColor: colors.primary,
    borderRadius: 12,
    paddingVertical: spacing.sm + 4,
    alignItems: "center",
  },
  uploadButtonText: { color: "#fff", fontSize: 15, fontWeight: "700" },
  list: { gap: spacing.sm, paddingTop: spacing.md, paddingBottom: spacing.xl },
  materialRow: { flexDirection: "row", alignItems: "center", gap: spacing.sm },
  materialEmoji: { fontSize: 22 },
  materialName: { fontSize: 14, fontWeight: "600", color: colors.textPrimary },
  materialMeta: { fontSize: 12, color: colors.textSecondary },
  emptyState: { flex: 1, backgroundColor: colors.background, padding: spacing.lg, justifyContent: "center" },
  emptyTitle: { fontSize: 18, fontWeight: "700", color: colors.textPrimary, marginBottom: spacing.xs },
  emptyBody: { fontSize: 14, color: colors.textSecondary, lineHeight: 20 },
});
