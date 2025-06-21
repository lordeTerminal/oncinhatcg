import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  Alert,
  Image,
} from 'react-native';
import axios from 'axios';

export default function Deck({ route }) {
  const { user_id } = route.params;
  const [cartas, setCartas] = useState([]);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    async function fetchDeck() {
      try {
        const res = await axios.get(`http://192.168.1.15:8000/api/deck/cartas/${user_id}`);
        setCartas(res.data);
      } catch (error) {
        console.error(error);
        Alert.alert('Erro', 'Não foi possível carregar o deck');
      } finally {
        setCarregando(false);
      }
    }

    fetchDeck();
  }, []);

  const renderItem = ({ item }: { item: any }) => (
    <View style={styles.card}>
      {item.imagem && (
        <Image
          source={{ uri: `http://192.168.1.15:8000/images/${item.imagem}` }}
          style={styles.imagem}
          resizeMode="contain"
        />
      )}
      <Text style={styles.nome}>{item.nome}</Text>
      <Text>Ataque: {item.ataque}</Text>
      <Text>HP: {item.hp}</Text>
      <Text>Mana: {item.mana}</Text>
      <Text>Efeitos: {item.efeitos}</Text>
      <Text>Descrição: {item.descricao}</Text>
    </View>
  );

  if (carregando) {
    return <Text style={{ marginTop: 50, textAlign: 'center' }}>Carregando deck...</Text>;
  }

  if (cartas.length === 0) {
    return <Text style={{ marginTop: 50, textAlign: 'center' }}>Seu deck está vazio.</Text>;
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
  container: {
    padding: 20,
  },
  card: {
    borderWidth: 1,
    borderColor: '#aaa',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
    backgroundColor: '#f9f9f9',
  },
  imagem: {
    width: '100%',
    height: 150,
    marginBottom: 10,
    borderRadius: 6,
  },
  nome: {
    fontWeight: 'bold',
    fontSize: 18,
    marginBottom: 5,
  },
});

