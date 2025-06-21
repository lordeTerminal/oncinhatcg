import mysql.connector
import random
from datetime import datetime
# Classe helper para imprimir e salvar em arquivo

class Logger:
    def __init__(self):
        data_str = datetime.now().strftime("%d%m%Y_%H%M%S")  # Data + hora:minuto:segundo
        self.filename = f"resultado_batalha_{data_str}.txt"
        self.file = open(self.filename, 'w', encoding='utf-8')
    def write(self, msg):
        print(msg)
        self.file.write(msg + '\n')
    def close(self):
        self.file.close()

# Conexão com o banco
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="golimar10*",
    database="cards"
)
cursor = conn.cursor(dictionary=True)

def obter_deck(jogador_id):
    query = """
    SELECT c.* FROM deck d
    JOIN carta c ON d.carta_id = c.id
    WHERE d.jogador_id = %s AND c.id <= 8
    """
    cursor.execute(query, (jogador_id,))
    return cursor.fetchall()

def batalha(deck1, deck2, logger):
    logger.write("\n🔥 BATALHA INICIADA! 🔥\n")
    rodada = 1
    while deck1 and deck2:
        logger.write(f"⚔️ Rodada {rodada}")
        carta1 = random.choice(deck1)
        carta2 = random.choice(deck2)

        logger.write(f"Jogador 1: {carta1['nome']} (ATK {carta1['ataque']}) VS Jogador 2: {carta2['nome']} (ATK {carta2['ataque']})")

        if carta1['ataque'] > carta2['ataque']:
            logger.write(f"✅ {carta1['nome']} venceu a rodada!")
            deck2.remove(carta2)
        elif carta2['ataque'] > carta1['ataque']:
            logger.write(f"❌ {carta2['nome']} venceu a rodada!")
            deck1.remove(carta1)
        else:
            logger.write("🤝 Empate! Ambas as cartas são descartadas.")
            deck1.remove(carta1)
            deck2.remove(carta2)

        rodada += 1
        logger.write("")

    logger.write("🏁 Fim da batalha!")
    if deck1 and not deck2:
        logger.write("🏆 Jogador 1 venceu!")
    elif deck2 and not deck1:
        logger.write("🏆 Jogador 2 venceu!")
    else:
        logger.write("⚖️ Empate total!")

if __name__ == "__main__":
    jogador1_id = 1
    jogador2_id = 2

    deck1 = obter_deck(jogador1_id)
    deck2 = obter_deck(jogador2_id)

    logger = Logger()

    if not deck1 or not deck2:
        logger.write("❗ Um ou ambos os decks estão vazios (id 1 a 8). Verifique no banco.")
    else:
        batalha(deck1, deck2, logger)

    logger.close()
    cursor.close()
    conn.close()

