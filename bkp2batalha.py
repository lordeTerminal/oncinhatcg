from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_db
import random

router = APIRouter()

# Modelos de entrada
class JogadaRequest(BaseModel):
    jogador_id: int
    carta_escolhida_id: int

class BotDeckRequest(BaseModel):
    jogador_id: int
    carta_ids: list[int]

# Estados em memória (temporariamente, para simplificação)
partidas_em_andamento = {}

# Representa uma carta durante a batalha
class CartaBatalha:
    def __init__(self, carta_dict):
        self.id = carta_dict["id"]
        self.nome = carta_dict["nome"]
        self.ataque = carta_dict["ataque"]
        self.hp = carta_dict["hp"]
        self.mana = carta_dict["mana"]
        self.efeitos = carta_dict.get("efeitos", "")
        self.descricao = carta_dict["descricao"]
        self.imagem = carta_dict.get("imagem", "")

    def to_dict(self):
        return self.__dict__

# Rota para gerar um deck aleatório para o bot (10 cartas)
@router.get("/bot/deck")
def gerar_deck_bot():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM carta")
    todas_cartas = cursor.fetchall()

    if not todas_cartas:
        raise HTTPException(status_code=400, detail="Não há cartas disponíveis")

    deck_bot = random.sample(todas_cartas, min(10, len(todas_cartas)))  # 10 cartas ou menos

    cursor.close()
    db.close()

    return [c["id"] for c in deck_bot]

# Rota para montar o deck do bot no banco
@router.post("/bot/deck/montar")
def montar_deck_bot(dados: BotDeckRequest):
    db = get_db()
    cursor = db.cursor()

    # Remove deck antigo do bot
    cursor.execute("DELETE FROM deck WHERE jogador_id=%s", (dados.jogador_id,))

    # Insere as cartas do novo deck
    for carta_id in dados.carta_ids:
        cursor.execute(
            "INSERT INTO deck (jogador_id, carta_id) VALUES (%s, %s)",
            (dados.jogador_id, carta_id)
        )

    db.commit()
    cursor.close()
    db.close()

    return {"msg": "Deck do bot montado com sucesso"}

# Inicializa a batalha
@router.post("/batalha/iniciar")
def iniciar_batalha(jogador_id: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Carrega o deck do jogador
    cursor.execute("""
        SELECT c.* FROM deck d
        JOIN carta c ON d.carta_id = c.id
        WHERE d.jogador_id = %s
    """, (jogador_id,))
    deck_jogador = [CartaBatalha(row) for row in cursor.fetchall()]

    if len(deck_jogador) == 0:
        raise HTTPException(status_code=400, detail="Deck do jogador está vazio")

    # Carrega o deck do bot (id fixo = 1)
    cursor.execute("""
        SELECT c.* FROM deck d
        JOIN carta c ON d.carta_id = c.id
        WHERE d.jogador_id = 1
    """)
    deck_bot = [CartaBatalha(row) for row in cursor.fetchall()]

    if len(deck_bot) == 0:
        raise HTTPException(status_code=400, detail="Deck do bot está vazio")

    random.shuffle(deck_jogador)
    random.shuffle(deck_bot)

    partida = {
        "jogador_id": jogador_id,
        "bot_id": 1,
        "hp_jogador": 100,
        "hp_bot": 100,
        "mao_jogador": deck_jogador[:3],
        "mao_bot": deck_bot[:3],
        "deck_jogador": deck_jogador[3:],
        "deck_bot": deck_bot[3:],
        "log": []
    }

    partidas_em_andamento[jogador_id] = partida
    return {
        "msg": "Batalha iniciada",
        "mao_jogador": [c.to_dict() for c in partida["mao_jogador"]]
    }

# Realiza uma jogada
@router.post("/batalha/jogada")
def jogada(dados: JogadaRequest):
    partida = partidas_em_andamento.get(dados.jogador_id)
    if not partida:
        raise HTTPException(status_code=404, detail="Batalha não encontrada")

    carta_jogador = next((c for c in partida["mao_jogador"] if c.id == dados.carta_escolhida_id), None)
    if not carta_jogador:
        raise HTTPException(status_code=400, detail="Carta não está na mão do jogador")

    carta_bot = random.choice(partida["mao_bot"])

    # Aplica dano simultâneo
    carta_bot.hp -= carta_jogador.ataque
    carta_jogador.hp -= carta_bot.ataque

    dano_jogador = max(0, -carta_jogador.hp)
    dano_bot = max(0, -carta_bot.hp)

    partida["hp_jogador"] -= dano_jogador
    partida["hp_bot"] -= dano_bot

    resultado = {
        "carta_jogador": carta_jogador.nome,
        "carta_bot": carta_bot.nome,
        "dano_jogador": dano_jogador,
        "dano_bot": dano_bot,
        "hp_restante_jogador": partida["hp_jogador"],
        "hp_restante_bot": partida["hp_bot"]
    }

    partida["log"].append(resultado)

    # Função para processar carta (remover da mão e devolver para o deck)
    def processar_carta(carta, mao, deck):
        mao.remove(carta)
        if carta.hp > 0:
            deck.insert(0, carta)  # volta ao topo do deck
        else:
            deck.append(carta)     # volta pro fundo do deck

    processar_carta(carta_jogador, partida["mao_jogador"], partida["deck_jogador"])
    processar_carta(carta_bot, partida["mao_bot"], partida["deck_bot"])

    # Compra cartas para manter 3 na mão
    while len(partida["mao_jogador"]) < 3 and partida["deck_jogador"]:
        partida["mao_jogador"].append(partida["deck_jogador"].pop(0))

    while len(partida["mao_bot"]) < 3 and partida["deck_bot"]:
        partida["mao_bot"].append(partida["deck_bot"].pop(0))

    fim = None
    if partida["hp_jogador"] <= 0:
        fim = "bot"
    elif partida["hp_bot"] <= 0:
        fim = "jogador"

    if fim:
        del partidas_em_andamento[dados.jogador_id]

    return {
        "resultado": resultado,
        "mao_jogador": [c.to_dict() for c in partida["mao_jogador"]],
        "fim": fim,
        "log": partida["log"]
    }

