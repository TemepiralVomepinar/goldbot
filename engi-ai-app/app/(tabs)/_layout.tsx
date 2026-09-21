import { Tabs } from "expo-router";
import { Text } from "react-native";
import { colors } from "@/lib/theme";

function TabIcon({ emoji, focused }: { emoji: string; focused: boolean }) {
  return <Text style={{ fontSize: 20, opacity: focused ? 1 : 0.5 }}>{emoji}</Text>;
}

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textSecondary,
      }}
    >
      <Tabs.Screen
        name="index"
        options={{ title: "Home", tabBarIcon: ({ focused }) => <TabIcon emoji="🏠" focused={focused} /> }}
      />
      <Tabs.Screen
        name="studio"
        options={{ title: "Studio", tabBarIcon: ({ focused }) => <TabIcon emoji="📚" focused={focused} /> }}
      />
      <Tabs.Screen
        name="ai"
        options={{ title: "AI", tabBarIcon: ({ focused }) => <TabIcon emoji="🤖" focused={focused} /> }}
      />
      <Tabs.Screen
        name="progressi"
        options={{ title: "Progressi", tabBarIcon: ({ focused }) => <TabIcon emoji="📊" focused={focused} /> }}
      />
      <Tabs.Screen
        name="profilo"
        options={{ title: "Profilo", tabBarIcon: ({ focused }) => <TabIcon emoji="👤" focused={focused} /> }}
      />
    </Tabs>
  );
}
