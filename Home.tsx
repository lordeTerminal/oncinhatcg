// Home.tsx
import React from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';

export default function Home({ route, navigation }) {
  const { user_id, nome } = route.params;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Bem-vindo, {nome}!</Text>
      <Text style={styles.subtitle}>ID do Jogador: {user_id}</Text>

      <Button
        title="Ver meu Deck"
        onPress={() => navigation.navigate('Deck', { user_id })}
      />
      <Button
        title="Escolher Cartas"
        onPress={() => navigation.navigate('Cartas', { user_id })}
      />
      <Button
        title="Batalhar"
        onPress={() => navigation.navigate('Batalha', { user_id })}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 20 },
  title: { fontSize: 24, textAlign: 'center', marginBottom: 10 },
  subtitle: { fontSize: 16, textAlign: 'center', marginBottom: 20 },
});

