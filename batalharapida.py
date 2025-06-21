import mysql.connector
import random
from datetime import datetime

class Logger:
    def __init__(self):
        data_str = datetime.now().strftime("%d%m%Y_%H%M%S")
        self.filename = f"resultado_batalha_{data_str}.txt"
        self.file = open(self.filename, 'w', encoding='utf-8')
    def write(self, msg):
        print(msg)
        self.file.write(msg + '\n')
    def close(self):
        self.file.close()

def gerar_deck_aleatorio(conn, jogador_id, tamanho_deck=5):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM carta")
    cartas = [row[0] for row in cursor.fetchall()]
    deck_aleatorio = random.sample(cartas, min(tamanho_deck, len(cartas)))

    cursor.execute("DELETE FROM deck WHERE jogador_id = %s", (jogador_id,))
    for carta_id in deck_aleatorio:
        cursor.execute("INSERT INTO deck (jogador_id, carta_id) VALUES (%s, %s)", (jogador_id, carta_id))
    conn.commit()
    cursor.close()
    return deck_aleatorio

def obter_deck(conn, jogador_id):
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT c.* FROM deck d
    JOIN carta c ON d.carta_id = c.id
    WHERE d.jogador_id = %s
    """
    cursor.execute(query, (jogador_id,))
    deck = cursor.fetchall()
    cursor.close()
    return deck

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
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="golimar10*",  # ajuste
        database="cards"
    )

    jogador1_id = int(input("Digite o ID do Jogador 1: "))
    jogador2_id = int(input("Digite o ID do Jogador 2: "))

    logger = Logger()

    gerar_deck_aleatorio(conn, jogador1_id)
    gerar_deck_aleatorio(conn, jogador2_id)

    deck1 = obter_deck(conn, jogador1_id)
    deck2 = obter_deck(conn, jogador2_id)

    if not deck1 or not deck2:
        logger.write("❗ Um ou ambos os decks estão vazios. Verifique o banco.")
    else:
        batalha(deck1, deck2, logger)

    logger.close()
    conn.close()

