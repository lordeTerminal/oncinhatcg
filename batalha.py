import mysql.connector
import random

# Conexão com o banco
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="golimar10*",
    database="cards"
)
cursor = db.cursor(dictionary=True)

# Funções
def buscar_deck(jogador_id):
    cursor.execute("""
        SELECT c.* FROM carta c
        JOIN deck d ON c.id = d.carta_id
        WHERE d.jogador_id = %s
    """, (jogador_id,))
    return cursor.fetchall()

def get_jogador(jogador_id):
    cursor.execute("SELECT * FROM jogador WHERE id = %s", (jogador_id,))
    return cursor.fetchone()

def atualizar_hp(jogador_id, novo_hp):
    cursor.execute("UPDATE jogador SET hp = %s WHERE id = %s", (novo_hp, jogador_id))
    db.commit()

def batalhar(carta1, carta2):
    print(f"\n{carta1['nome']} (HP: {carta1['hp']}) VS {carta2['nome']} (HP: {carta2['hp']})")

    if carta1['hp'] > carta2['hp']:
        dano = carta1['hp'] - carta2['hp']
        vencedor = 1
    elif carta2['hp'] > carta1['hp']:
        dano = carta2['hp'] - carta1['hp']
        vencedor = 2
    else:
        # Desempate pela mana
        if carta1['mana'] < carta2['mana']:
            dano = 1
            vencedor = 1
        elif carta2['mana'] < carta1['mana']:
            dano = 1
            vencedor = 2
        else:
            print("Empate total!")
            return None, 0

    print(f"Jogador {vencedor} vence e causa {dano} de dano!")
    return vencedor, dano

# Início da simulação
deck1 = buscar_deck(1)
deck2 = buscar_deck(2)
j1 = get_jogador(1)
j2 = get_jogador(2)

random.shuffle(deck1)
random.shuffle(deck2)

rodada = 1

while j1['hp'] > 0 and j2['hp'] > 0 and deck1 and deck2:
    print(f"\n--- Rodada {rodada} ---")
    carta1 = deck1.pop()
    carta2 = deck2.pop()
    
    vencedor, dano = batalhar(carta1, carta2)

    if vencedor == 1:
        j2['hp'] -= dano
    elif vencedor == 2:
        j1['hp'] -= dano

    rodada += 1

print("\n--- Fim da batalha ---")
print(f"Jogador 1 HP: {j1['hp']}")
print(f"Jogador 2 HP: {j2['hp']}")

if j1['hp'] > j2['hp']:
    print("Jogador 1 venceu!")
elif j2['hp'] > j1['hp']:
    print("Jogador 2 venceu!")
else:
    print("Empate!")
