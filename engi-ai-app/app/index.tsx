import { Redirect } from "expo-router";
import { ActivityIndicator, View } from "react-native";
import { useAuth } from "@/context/AuthContext";
import { colors } from "@/lib/theme";

export default function EntryPoint() {
  const { session, loading, supabaseReady } = useAuth();

  if (loading) {
    return (
      <View style={{ flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: colors.background }}>
        <ActivityIndicator color={colors.primary} />
      </View>
    );
  }

  // Senza Supabase configurato saltiamo l'auth e mostriamo comunque l'app
  // (utile per esplorare l'MVP con i dati demo prima di collegare un progetto reale).
  if (!supabaseReady || session) {
    return <Redirect href="/(tabs)" />;
  }

  return <Redirect href="/(auth)/login" />;
}
