import React, { useState } from 'react';
import {
  View,
  Text,
  Button,
  StyleSheet,
  ScrollView,
  Alert,
} from 'react-native';
import axios from 'axios';

export default function Batalha({ route }) {
  const { user_id } = route.params; // jogador real
  const BOT_JOGADOR_ID = 1; // bot fixo

  const [resultado, setResultado] = useState(null);

  const batalharContraBot = async () => {
    try {
      // 1. Pega o tamanho do deck do jogador real
      const resDeckJogador = await axios.get(`http://192.168.1.15:8000/api/deck/${user_id}`);
      const tamanhoDeck = resDeckJogador.data.length;

      // 2. Monta deck do bot com mesmo número de cartas (sem especificar cartas - backend escolhe aleatórias)
      await axios.post("http://192.168.1.15:8000/api/bot/deck/montar", {
        jogador_id: BOT_JOGADOR_ID,
        carta_ids: [], // vazio para o backend sortear
      });

      // 3. Realiza a batalha
      const resBatalha = await axios.post("http://192.168.1.15:8000/api/batalha", {
        jogador1_id: user_id,
        jogador2_id: BOT_JOGADOR_ID,
      });

      setResultado(resBatalha.data);
    } catch (error) {
      console.error(error);
      Alert.alert('Erro', error?.response?.data?.detail || 'Erro na batalha contra o bot');
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.titulo}>Batalha contra o Bot</Text>
      <Button title="Batalhar!" onPress={batalharContraBot} />

      {resultado && (
        <>
          <Text style={styles.resultado}>Vencedor: {resultado.resultado}</Text>
          <Text style={styles.resultado}>Pontos Jogador 1: {resultado.pontos1}</Text>
          <Text style={styles.resultado}>Pontos Bot: {resultado.pontos2}</Text>
          {resultado.log.map((r: any, idx: number) => (
            <View key={idx} style={styles.log}>
              <Text>Rodada {r.rodada}</Text>
              <Text>{r.carta1} x {r.carta2}</Text>
              <Text>{r.resultado}</Text>
            </View>
          ))}
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20 },
  titulo: { fontSize: 24, fontWeight: 'bold', marginBottom: 20 },
  resultado: { fontSize: 16, marginTop: 10 },
  log: {
    marginTop: 10,
    padding: 10,
    backgroundColor: '#f0f0f0',
    borderRadius: 6,
  },
});

