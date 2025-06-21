import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  Alert,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';
import axios from 'axios';

export default function Cartas({ route }) {
  const { user_id } = route.params;
  const [cartas, setCartas] = useState([]);
  const [cartasNoDeck, setCartasNoDeck] = useState<Set<number>>(new Set());
  const [carregando, setCarregando] = useState(true);

  const fetchCartas = async () => {
    try {
      const res = await axios.get('http://192.168.1.15:8000/api/cartas');
      setCartas(res.data);
    } catch (error) {
      console.error(error);
      Alert.alert('Erro', 'Falha ao carregar cartas');
    }
  };

  const fetchDeck = async () => {
    try {
      const res = await axios.get(`http://192.168.1.15:8000/api/deck/${user_id}`);
      setCartasNoDeck(new Set(res.data));
    } catch (error) {
      console.error(error);
      Alert.alert('Erro', 'Falha ao carregar deck');
    }
  };

  useEffect(() => {
    async function fetchAll() {
      await fetchCartas();
      await fetchDeck();
      setCarregando(false);
    }
    fetchAll();
  }, []);

  const adicionarCarta = async (carta_id: number) => {
    try {
      await axios.post('http://192.168.1.15:8000/api/deck/adicionar', {
        jogador_id: user_id,
        carta_id,
      });
      setCartasNoDeck(prev => new Set([...prev, carta_id]));
    } catch (error: any) {
      console.error(error);
      Alert.alert('Erro', error?.response?.data?.detail || 'Erro ao adicionar carta');
    }
  };

  const removerCarta = async (carta_id: number) => {
    try {
      await axios.post('http://192.168.1.15:8000/api/deck/remover', {
        jogador_id: user_id,
        carta_id,
      });
      setCartasNoDeck(prev => {
        const novoSet = new Set(prev);
        novoSet.delete(carta_id);
        return novoSet;
      });
    } catch (error) {
      console.error(error);
      Alert.alert('Erro', 'Erro ao remover carta');
    }
  };

  const renderItem = ({ item }: { item: any }) => {
    const noDeck = cartasNoDeck.has(item.id);

    return (
      <View style={styles.card}>
        <Text style={styles.nome}>{item.nome}</Text>
        <Text>Ataque: {item.ataque}</Text>
        <Text>HP: {item.hp}</Text>
        <Text>Mana: {item.mana}</Text>
        <Text>Efeitos: {item.efeitos}</Text>
        <Text>Descrição: {item.descricao}</Text>

        <TouchableOpacity
          style={[styles.button, noDeck ? styles.remover : styles.adicionar]}
          onPress={() =>
            noDeck ? removerCarta(item.id) : adicionarCarta(item.id)
          }
        >
          <Text style={styles.buttonText}>
            {noDeck ? 'Remover do Deck' : 'Adicionar ao Deck'}
          </Text>
        </TouchableOpacity>
      </View>
    );
  };

  if (carregando) {
    return <Text style={{ marginTop: 50, textAlign: 'center' }}>Carregando cartas...</Text>;
  }

  return (
    <FlatList
      data={cartas}
      keyExtractor={(item) => item.id.toString()}
      renderItem={renderItem}
      contentContainerStyle={styles.container}
    />
  );
}

const styles = StyleSheet.create({
  container: { padding: 20 },
  card: {
    borderWidth: 1,
    borderColor: '#aaa',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
    backgroundColor: '#fafafa',
  },
  nome: { fontWeight: 'bold', fontSize: 18, marginBottom: 5 },
  button: {
    marginTop: 10,
    padding: 10,
    borderRadius: 6,
  },
  buttonText: { color: 'white', textAlign: 'center', fontWeight: 'bold' },
  adicionar: {
    backgroundColor: '#4CAF50',
  },
  remover: {
    backgroundColor: '#E53935',
  },
});

