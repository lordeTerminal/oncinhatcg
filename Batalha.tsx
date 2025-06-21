import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  Alert,
  Image,
  TouchableOpacity,
  Modal,
  Animated,
  Easing,
} from "react-native";
import axios from "axios";

export default function Batalha({ route }) {
  const { user_id } = route.params;
  const BOT_ID = 1;

  const [jogadorMao, setJogadorMao] = useState([]);
  const [jogadorVida, setJogadorVida] = useState(100);
  const [botMao, setBotMao] = useState([]);
  const [botVida, setBotVida] = useState(100);
  const [log, setLog] = useState([]);
  const [rodada, setRodada] = useState(1);
  const [loading, setLoading] = useState(false);
  const [mensagemFim, setMensagemFim] = useState(null);
  const [animValor] = useState(new Animated.Value(0));
  const [cartasAnimadas, setCartasAnimadas] = useState({});

  useEffect(() => {
    iniciarBatalha();
  }, []);

  async function iniciarBatalha() {
    try {
      setLoading(true);
      // Inicia a batalha no backend, recebendo a mão inicial e vida
      const res = await axios.post(
        `http://192.168.1.15:8000/api/batalha/iniciar?jogador_id=${user_id}`
      );

      setJogadorMao(res.data.mao_jogador);
      setJogadorVida(res.data.hp_jogador);
      setBotVida(res.data.hp_bot);
      setLog([]);
      setRodada(1);
      setMensagemFim(null);
    } catch (error) {
      Alert.alert("Erro", "Não foi possível iniciar a batalha");
    } finally {
      setLoading(false);
    }
  }

  async function atacar(cartaJogador) {
    if (mensagemFim) return; // bloqueia se jogo terminou

    try {
      setLoading(true);
      // Envia jogada para backend
      const res = await axios.post("http://192.168.1.15:8000/api/batalha/jogada", {
        jogador_id: user_id,
        carta_escolhida_id: cartaJogador.id,
      });

      // Atualiza estados com dados do backend
      const data = res.data;

      // Animação simples: fadeIn para carta do jogador e bot
      animarCartas(cartaJogador.id, data.resultado.carta_bot);

      setJogadorMao(data.mao_jogador);
      setJogadorVida(data.hp_jogador);
      setBotVida(data.hp_bot);
      setLog((prev) => [...prev, { rodada, ...data.resultado }]);
      setRodada((r) => r + 1);

      if (data.fim) {
        setMensagemFim(data.mensagem_fim);
      }
    } catch (error) {
      Alert.alert("Erro", "Erro ao realizar jogada");
    } finally {
      setLoading(false);
    }
  }

  function animarCartas(idJogador, nomeCartaBot) {
    animValor.setValue(0);
    Animated.timing(animValor, {
      toValue: 1,
      duration: 800,
      easing: Easing.linear,
      useNativeDriver: true,
    }).start();
    // Você pode melhorar adicionando mais lógica para animar as cartas específicas
  }

  // Modal para mensagem de fim de jogo
  function ModalFimJogo() {
    return (
      <Modal transparent visible={!!mensagemFim} animationType="fade">
        <View style={styles.modalContainer}>
          <View style={styles.modalBox}>
            <Text style={styles.modalTexto}>{mensagemFim}</Text>
            <TouchableOpacity
              style={styles.botaoModal}
              onPress={() => iniciarBatalha()}
            >
              <Text style={styles.botaoTexto}>Jogar Novamente</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.titulo}>Batalha contra o Bot</Text>
      <Text style={styles.vida}>Sua Vida: {jogadorVida}</Text>
      <Text style={styles.vida}>Vida do Bot: {botVida}</Text>

      <Text style={styles.subtitulo}>Sua Mão:</Text>
      <View style={styles.maoContainer}>
        {jogadorMao.map((carta) => (
          <TouchableOpacity
            key={carta.id}
            style={styles.card}
            onPress={() => atacar(carta)}
            disabled={loading || !!mensagemFim}
          >
            {carta.imagem && (
              <Image
                source={{ uri: `http://192.168.1.15:8000/images/${carta.imagem}` }}
                style={styles.imagem}
              />
            )}
            <Text style={styles.nome}>{carta.nome}</Text>
            <Text>Ataque: {carta.ataque}</Text>
            <Text>HP: {carta.hp}</Text>
            <Text>Mana: {carta.mana}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.subtitulo}>Log:</Text>
      <View style={{ maxHeight: 150 }}>
        {log.slice(-5).map((item, idx) => (
          <Text key={idx} style={styles.logText}>
            Rodada {item.rodada}: {item.carta_jogador} causou {item.dano_bot} ao Bot,{" "}
            {item.carta_bot} causou {item.dano_jogador} a você
          </Text>
        ))}
      </View>

      <ModalFimJogo />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20, flex: 1, backgroundColor: "#f0f0f0" },
  titulo: { fontSize: 24, fontWeight: "bold", marginBottom: 20, textAlign: "center" },
  vida: { fontSize: 16, marginBottom: 10, textAlign: "center" },
  subtitulo: { fontSize: 18, fontWeight: "600", marginTop: 20, marginBottom: 10 },
  maoContainer: { flexDirection: "row", flexWrap: "wrap", justifyContent: "center", gap: 10 },
  card: {
    width: 150,
    borderWidth: 1,
    borderColor: "#aaa",
    borderRadius: 8,
    padding: 10,
    backgroundColor: "#fff",
    marginRight: 10,
    marginTop: 10,
    alignItems: "center",
  },
  imagem: { width: "100%", height: 100, marginBottom: 10 },
  nome: { fontWeight: "bold", fontSize: 16, textAlign: "center" },
  logText: { fontSize: 14, marginBottom: 4, textAlign: "center" },

  modalContainer: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.7)",
    justifyContent: "center",
    alignItems: "center",
  },
  modalBox: {
    backgroundColor: "#fff",
    borderRadius: 10,
    padding: 30,
    width: "80%",
    alignItems: "center",
  },
  modalTexto: {
    fontSize: 20,
    fontWeight: "bold",
    marginBottom: 20,
    textAlign: "center",
  },
  botaoModal: {
    backgroundColor: "#007bff",
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 8,
  },
  botaoTexto: {
    color: "#fff",
    fontWeight: "bold",
  },
});

