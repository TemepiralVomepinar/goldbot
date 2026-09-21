import { Stack } from "expo-router";
import { colors } from "@/lib/theme";

export default function ProfiloLayout() {
  return (
    <Stack
      screenOptions={{
        headerStyle: { backgroundColor: colors.background },
        headerShadowVisible: false,
        headerTintColor: colors.textPrimary,
      }}
    >
      <Stack.Screen name="index" options={{ title: "Profilo" }} />
      <Stack.Screen name="impostazioni-ai" options={{ title: "Impostazioni AI" }} />
    </Stack>
  );
}
