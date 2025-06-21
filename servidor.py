import socket
import threading
import mysql.connector
import random
from datetime import datetime

PORTA = 5555
HOST = '0.0.0.0'

class Jogador:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.id = None
        self.nome = None
        self.hp = 0
        self.defesa = 0
        self.deck = []
        self.mana = 5

# Função utilitária para enviar e receber dados

def enviar(jogador, msg):
    jogador.conn.sendall((msg + '\n').encode())

def receber(jogador):
    return jogador.conn.recv(1024).decode().strip()

# Banco de dados
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="golimar10*",
    database="cards"
)
cursor = conn.cursor(dictionary=True)

def carregar_jogador(jogador, id_jogador):
    cursor.execute("SELECT * FROM jogador WHERE id = %s", (id_jogador,))
    dados = cursor.fetchone()
    if dados:
        jogador.id = id_jogador
        jogador.nome = dados['nome']
        jogador.hp = dados['hp']
        jogador.defesa = dados['defesa']
        cursor.execute("""
            SELECT c.* FROM deck d
            JOIN carta c ON d.carta_id = c.id
            WHERE d.jogador_id = %s
        """, (id_jogador,))
        jogador.deck = cursor.fetchall()
        return True
    return False

def escolha_carta(jogador):
    cartas = [c for c in jogador.deck if c['mana'] <= jogador.mana]
    enviar(jogador, f"Mana disponível: {jogador.mana}")
    for idx, carta in enumerate(cartas):
        enviar(jogador, f"{idx+1}. {carta['nome']} (ATK {carta['ataque']}, MANA {carta['mana']})")
    enviar(jogador, "Escolha sua carta (número):")
    try:
        escolha = int(receber(jogador)) - 1
        return cartas[escolha] if 0 <= escolha < len(cartas) else None
    except:
        return None

def batalha(j1, j2):
    rodada = 1
    while j1.hp > 0 and j2.hp > 0 and j1.deck and j2.deck:
        enviar(j1, f"\n--- Rodada {rodada} ---")
        enviar(j2, f"\n--- Rodada {rodada} ---")

        j1.mana = min(j1.mana + 1, 10)
        j2.mana = min(j2.mana + 1, 10)

        carta1 = escolha_carta(j1)
        carta2 = escolha_carta(j2)

        if carta1:
            j1.mana -= carta1['mana']
        if carta2:
            j2.mana -= carta2['mana']

        nome1 = carta1['nome'] if carta1 else "(sem carta)"
        nome2 = carta2['nome'] if carta2 else "(sem carta)"
        atk1 = carta1['ataque'] if carta1 else 0
        atk2 = carta2['ataque'] if carta2 else 0

        enviar(j1, f"{nome1} (ATK {atk1}) vs {nome2} (ATK {atk2})")
        enviar(j2, f"{nome1} (ATK {atk1}) vs {nome2} (ATK {atk2})")

        if atk1 > atk2:
            dano = max(0, atk1 - j2.defesa)
            j2.hp -= dano
            enviar(j1, f"Você venceu a rodada! {j2.nome} perde {dano} HP (agora: {j2.hp})")
            enviar(j2, f"Você perdeu a rodada! {j2.nome} perde {dano} HP (agora: {j2.hp})")
            if carta2: j2.deck.remove(carta2)
        elif atk2 > atk1:
            dano = max(0, atk2 - j1.defesa)
            j1.hp -= dano
            enviar(j1, f"Você perdeu a rodada! {j1.nome} perde {dano} HP (agora: {j1.hp})")
            enviar(j2, f"Você venceu a rodada! {j1.nome} perde {dano} HP (agora: {j1.hp})")
            if carta1: j1.deck.remove(carta1)
        else:
            enviar(j1, "Empate! Cartas descartadas.")
            enviar(j2, "Empate! Cartas descartadas.")
            if carta1: j1.deck.remove(carta1)
            if carta2: j2.deck.remove(carta2)

        rodada += 1

    if j1.hp <= 0 and j2.hp <= 0:
        enviar(j1, "Empate total!")
        enviar(j2, "Empate total!")
    elif j1.hp <= 0:
        enviar(j1, f"Você perdeu! {j2.nome} venceu!")
        enviar(j2, f"Você venceu! {j2.nome} venceu!")
    elif j2.hp <= 0:
        enviar(j1, f"Você venceu! {j1.nome} venceu!")
        enviar(j2, f"Você perdeu! {j1.nome} venceu!")
    else:
        enviar(j1, "Fim de cartas! Vitória por resistência!")
        enviar(j2, "Fim de cartas! Vitória por resistência!")

def lidar_com_jogador(conn, addr, jogador, pronto_evento):
    jogador.conn = conn
    jogador.addr = addr
    enviar(jogador, "Informe seu ID de jogador:")
    id_j = int(receber(jogador))
    if carregar_jogador(jogador, id_j):
        enviar(jogador, f"Bem-vindo, {jogador.nome}!")
        pronto_evento.set()
    else:
        enviar(jogador, "ID inválido. Encerrando.")
        jogador.conn.close()

print(f"Servidor escutando em {HOST}:{PORTA} ...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORTA))
s.listen(2)

jogador1 = Jogador(None, None)
jogador2 = Jogador(None, None)
evento1 = threading.Event()
evento2 = threading.Event()

conn1, addr1 = s.accept()
threading.Thread(target=lidar_com_jogador, args=(conn1, addr1, jogador1, evento1)).start()

conn2, addr2 = s.accept()
threading.Thread(target=lidar_com_jogador, args=(conn2, addr2, jogador2, evento2)).start()

evento1.wait()
evento2.wait()
batalha(jogador1, jogador2)

jogador1.conn.close()
jogador2.conn.close()
s.close()

