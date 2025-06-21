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

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="golimar10*",  # troque se necessário
    database="cards"
)
cursor = conn.cursor(dictionary=True)

def obter_jogador(jogador_id):
    cursor.execute("SELECT * FROM jogador WHERE id = %s", (jogador_id,))
    return cursor.fetchone()

def obter_deck(jogador_id):
    cursor.execute("""
        SELECT c.* FROM deck d
        JOIN carta c ON d.carta_id = c.id
        WHERE d.jogador_id = %s
    """, (jogador_id,))
    return cursor.fetchall()

def batalha_completa(j1_id, j2_id, logger):
    jogador1 = obter_jogador(j1_id)
    jogador2 = obter_jogador(j2_id)

    deck1 = obter_deck(j1_id)
    deck2 = obter_deck(j2_id)

    if not deck1 or not deck2:
        logger.write("❗ Um ou ambos os decks estão vazios. Verifique no banco.")
        return

    hp1, def1 = jogador1['hp'], jogador1['defesa']
    hp2, def2 = jogador2['hp'], jogador2['defesa']
    mana1 = mana2 = 5
    rodada = 1

    logger.write(f"\n🎮 Jogador 1: {jogador1['nome']} (HP {hp1}, DEF {def1})")
    logger.write(f"🎮 Jogador 2: {jogador2['nome']} (HP {hp2}, DEF {def2})\n")

    while hp1 > 0 and hp2 > 0 and deck1 and deck2:
        logger.write(f"⚔️ Rodada {rodada}")
        mana1 = min(mana1 + 1, 10)
        mana2 = min(mana2 + 1, 10)

        cartas1 = [c for c in deck1 if c['mana'] <= mana1]
        cartas2 = [c for c in deck2 if c['mana'] <= mana2]

        carta1 = random.choice(cartas1) if cartas1 else None
        carta2 = random.choice(cartas2) if cartas2 else None

        nome1 = carta1['nome'] if carta1 else "(sem carta)"
        nome2 = carta2['nome'] if carta2 else "(sem carta)"
        atk1 = carta1['ataque'] if carta1 else 0
        atk2 = carta2['ataque'] if carta2 else 0

        if carta1:
            mana1 -= carta1['mana']
        if carta2:
            mana2 -= carta2['mana']

        logger.write(f"{nome1} (ATK {atk1}) vs {nome2} (ATK {atk2})")

        if atk1 > atk2:
            dano = max(0, atk1 - def2)
            hp2 -= dano
            logger.write(f"✅ {nome1} venceu a rodada! Jogador 2 perde {dano} HP (restante: {hp2})")
            if carta2: deck2.remove(carta2)
        elif atk2 > atk1:
            dano = max(0, atk2 - def1)
            hp1 -= dano
            logger.write(f"❌ {nome2} venceu a rodada! Jogador 1 perde {dano} HP (restante: {hp1})")
            if carta1: deck1.remove(carta1)
        else:
            logger.write("🤝 Empate! Ambas as cartas são descartadas.")
            if carta1: deck1.remove(carta1)
            if carta2: deck2.remove(carta2)

        rodada += 1

    logger.write("\n🏁 Fim da batalha!")
    if hp1 <= 0 and hp2 <= 0:
        logger.write("⚖️ Empate total!")
    elif hp1 <= 0:
        logger.write(f"🏆 {jogador2['nome']} venceu!")
    elif hp2 <= 0:
        logger.write(f"🏆 {jogador1['nome']} venceu!")
    else:
        logger.write("🧩 Cartas acabaram! Vitória por HP!")
        if hp1 > hp2:
            logger.write(f"🏆 {jogador1['nome']} venceu por HP!")
        elif hp2 > hp1:
            logger.write(f"🏆 {jogador2['nome']} venceu por HP!")
        else:
            logger.write("⚖️ Empate de resistência!")

if __name__ == "__main__":
    logger = Logger()
    j1 = int(input("ID do Jogador 1: "))
    j2 = int(input("ID do Jogador 2: "))
    batalha_completa(j1, j2, logger)
    logger.close()
    cursor.close()
    conn.close()

