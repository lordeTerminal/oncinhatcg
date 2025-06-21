import socket
import threading
import mysql.connector
import random
from datetime import datetime
import copy

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
        self.carta_ativa = None

# Função utilitária para enviar e receber dados

def enviar(jogador, msg):
    try:
        jogador.conn.sendall((msg + '\n').encode())
    except:
        pass

def receber(jogador):
    try:
        return jogador.conn.recv(1024).decode().strip()
    except:
        return ""

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
        jogador.deck = [copy.deepcopy(carta) for carta in cursor.fetchall()]
        return True
    return False

def escolha_carta(jogador):
    cartas = [c for c in jogador.deck if c['mana'] <= jogador.mana]
    if not cartas:
        enviar(jogador, "Sem cartas disponíveis com a mana atual.")
        return None
    enviar(jogador, f"Mana disponível: {jogador.mana}")
    for idx, carta in enumerate(cartas):
        enviar(jogador, f"{idx+1}. {carta['nome']} (ATK {carta['ataque']}, HP {carta['hp']}, MANA {carta['mana']})")
    enviar(jogador, "Escolha sua carta (número):")
    try:
        escolha = int(receber(jogador)) - 1
        carta_escolhida = cartas[escolha] if 0 <= escolha < len(cartas) else None
        return copy.deepcopy(carta_escolhida) if carta_escolhida else None
    except:
        return None

def batalha(j1, j2):
    rodada = 1
    while j1.hp > 0 and j2.hp > 0 and j1.deck and j2.deck:
        enviar(j1, f"\n--- Rodada {rodada} ---")
        enviar(j2, f"\n--- Rodada {rodada} ---")

        j1.mana = min(j1.mana + 1, 10)
        j2.mana = min(j2.mana + 1, 10)

        if not j1.carta_ativa or j1.carta_ativa['hp'] <= 0:
            j1.carta_ativa = escolha_carta(j1)
            if j1.carta_ativa:
                j1.mana -= j1.carta_ativa['mana']
        if not j2.carta_ativa or j2.carta_ativa['hp'] <= 0:
            j2.carta_ativa = escolha_carta(j2)
            if j2.carta_ativa:
                j2.mana -= j2.carta_ativa['mana']

        if not j1.carta_ativa or not j2.carta_ativa:
            break

        nome1 = j1.carta_ativa['nome']
        nome2 = j2.carta_ativa['nome']
        atk1 = j1.carta_ativa['ataque']
        atk2 = j2.carta_ativa['ataque']

        enviar(j1, f"{nome1} (HP {j1.carta_ativa['hp']}) vs {nome2} (HP {j2.carta_ativa['hp']})")
        enviar(j2, f"{nome1} (HP {j1.carta_ativa['hp']}) vs {nome2} (HP {j2.carta_ativa['hp']})")

        # Ataques simultâneos
        j2.carta_ativa['hp'] -= atk1
        enviar(j1, f"Você causou {atk1} de dano a {nome2}.")
        enviar(j2, f"{nome1} causou {atk1} de dano a sua carta.")
        if j2.carta_ativa['hp'] <= 0:
            excedente = abs(j2.carta_ativa['hp'])
            j2.hp -= excedente
            enviar(j1, f"Dano excedente: {excedente} aplicado ao jogador {j2.nome} (HP {j2.hp})")
            enviar(j2, f"Sua carta foi destruída! Dano excedente: {excedente} aplicado a você (HP {j2.hp})")
            try:
                j2.deck.remove(next(c for c in j2.deck if c['id'] == j2.carta_ativa['id']))
            except StopIteration:
                pass
            j2.carta_ativa = None

        j1.carta_ativa['hp'] -= atk2
        enviar(j2, f"Você causou {atk2} de dano a {nome1}.")
        enviar(j1, f"{nome2} causou {atk2} de dano a sua carta.")
        if j1.carta_ativa['hp'] <= 0:
            excedente = abs(j1.carta_ativa['hp'])
            j1.hp -= excedente
            enviar(j2, f"Dano excedente: {excedente} aplicado ao jogador {j1.nome} (HP {j1.hp})")
            enviar(j1, f"Sua carta foi destruída! Dano excedente: {excedente} aplicado a você (HP {j1.hp})")
            try:
                j1.deck.remove(next(c for c in j1.deck if c['id'] == j1.carta_ativa['id']))
            except StopIteration:
                pass
            j1.carta_ativa = None

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
    try:
        id_j = int(receber(jogador))
    except:
        enviar(jogador, "ID inválido.")
        jogador.conn.close()
        return

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

