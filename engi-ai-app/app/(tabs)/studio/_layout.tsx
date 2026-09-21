import { Stack } from "expo-router";
import { colors } from "@/lib/theme";

export default function StudioLayout() {
  return (
    <Stack
      screenOptions={{
        headerStyle: { backgroundColor: colors.background },
        headerShadowVisible: false,
        headerTintColor: colors.textPrimary,
      }}
    >
      <Stack.Screen name="index" options={{ title: "Studio" }} />
      <Stack.Screen name="materie/index" options={{ title: "Le mie materie" }} />
      <Stack.Screen name="materie/[subjectId]/index" options={{ title: "" }} />
      <Stack.Screen name="materie/[subjectId]/[topicId]" options={{ title: "" }} />
      <Stack.Screen name="esercizi/index" options={{ title: "Esercizi" }} />
      <Stack.Screen name="materiali/index" options={{ title: "Materiali" }} />
      <Stack.Screen name="piano" options={{ title: "Piano di studio AI" }} />
      <Stack.Screen name="strumenti" options={{ title: "Strumenti" }} />
      <Stack.Screen name="esami" options={{ title: "Simulazione d'esame" }} />
    </Stack>
  );
}
