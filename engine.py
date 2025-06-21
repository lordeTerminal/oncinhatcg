import mysql.connector
import random

# Conexão com o banco
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="golimar10*",  # <--- troque pela sua senha real
    database="cards"
)
cursor = conn.cursor(dictionary=True)

# Função para obter o deck de criaturas (id 1 a 8) de um jogador
def obter_deck(jogador_id):
    query = """
    SELECT c.* FROM deck d
    JOIN carta c ON d.carta_id = c.id
    WHERE d.jogador_id = %s AND c.id <= 8
    """
    cursor.execute(query, (jogador_id,))
    return cursor.fetchall()

# Simulação de batalha entre dois decks
def batalha(deck1, deck2):
    print("\n🔥 BATALHA INICIADA! 🔥\n")
    rodada = 1
    while deck1 and deck2:
        print(f"⚔️ Rodada {rodada}")
        carta1 = random.choice(deck1)
        carta2 = random.choice(deck2)

        print(f"Jogador 1: {carta1['nome']} (ATK {carta1['ataque']}) VS Jogador 2: {carta2['nome']} (ATK {carta2['ataque']})")

        if carta1['ataque'] > carta2['ataque']:
            print(f"✅ {carta1['nome']} venceu a rodada!")
            deck2.remove(carta2)
        elif carta2['ataque'] > carta1['ataque']:
            print(f"❌ {carta2['nome']} venceu a rodada!")
            deck1.remove(carta1)
        else:
            print("🤝 Empate! Ambas as cartas são descartadas.")
            deck1.remove(carta1)
            deck2.remove(carta2)

        rodada += 1
        print()

    print("🏁 Fim da batalha!")
    if deck1 and not deck2:
        print("🏆 Jogador 1 venceu!")
    elif deck2 and not deck1:
        print("🏆 Jogador 2 venceu!")
    else:
        print("⚖️ Empate total!")

# IDs dos jogadores
jogador1_id = 1
jogador2_id = 2

# Obter decks
deck1 = obter_deck(jogador1_id)
deck2 = obter_deck(jogador2_id)

# Verificação
if not deck1 or not deck2:
    print("❗ Um ou ambos os decks estão vazios (id 1 a 8). Verifique no banco.")
else:
    batalha(deck1, deck2)

# Fechar conexão
cursor.close()
conn.close()

