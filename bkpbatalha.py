from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_db
import random

router = APIRouter()

class BatalhaRequest(BaseModel):
    jogador1_id: int
    jogador2_id: int

class BotDeckRequest(BaseModel):
    jogador_id: int
    carta_ids: list[int]

@router.post("/batalha")
def realizar_batalha(dados: BatalhaRequest):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.* FROM deck d
        JOIN carta c ON d.carta_id = c.id
        WHERE d.jogador_id = %s
    """, (dados.jogador1_id,))
    cartas1 = cursor.fetchall()

    cursor.execute("""
        SELECT c.* FROM deck d
        JOIN carta c ON d.carta_id = c.id
        WHERE d.jogador_id = %s
    """, (dados.jogador2_id,))
    cartas2 = cursor.fetchall()

    if len(cartas1) == 0 or len(cartas2) == 0:
        raise HTTPException(status_code=400, detail="Ambos os jogadores devem ter cartas no deck")

    rounds = min(len(cartas1), len(cartas2))
    pontos1 = 0
    pontos2 = 0
    log = []

    for i in range(rounds):
        c1 = cartas1[i]
        c2 = cartas2[i]

        dano1 = c1["ataque"]
        dano2 = c2["ataque"]

        hp1 = c1["hp"] - dano2
        hp2 = c2["hp"] - dano1

        if hp1 > hp2:
            pontos1 += 1
            resultado = "Jogador 1 venceu a rodada"
        elif hp2 > hp1:
            pontos2 += 1
            resultado = "Jogador 2 venceu a rodada"
        else:
            resultado = "Empate na rodada"

        log.append({
            "rodada": i + 1,
            "carta1": c1["nome"],
            "carta2": c2["nome"],
            "resultado": resultado
        })

    if pontos1 > pontos2:
        vencedor = "jogador1"
    elif pontos2 > pontos1:
        vencedor = "jogador2"
    else:
        vencedor = "empate"

    cursor.execute("SELECT nome FROM jogador WHERE id = %s", (dados.jogador1_id,))
    nome1 = cursor.fetchone()["nome"]

    cursor.execute("SELECT nome FROM jogador WHERE id = %s", (dados.jogador2_id,))
    nome2 = cursor.fetchone()["nome"]

    vencedor_nome = nome1 if vencedor == "jogador1" else nome2 if vencedor == "jogador2" else "empate"

    cursor.execute(
        "INSERT INTO resultado (jogador1, jogador2, vencedor) VALUES (%s, %s, %s)",
        (nome1, nome2, vencedor_nome)
    )
    db.commit()
    cursor.close()
    db.close()

    return {
        "resultado": vencedor_nome,
        "pontos1": pontos1,
        "pontos2": pontos2,
        "log": log
    }

@router.post("/bot/deck/montar")
def montar_deck_bot(dados: BotDeckRequest):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Primeiro, pega o tamanho do deck do jogador oponente
    cursor.execute("SELECT COUNT(*) as count FROM deck WHERE jogador_id = %s", (dados.jogador_id,))
    tamanho_deck = cursor.fetchone()["count"]

    # Pega todas as cartas disponíveis
    cursor.execute("SELECT id FROM carta")
    todas_cartas = cursor.fetchall()
    if not todas_cartas:
        raise HTTPException(status_code=400, detail="Não há cartas disponíveis")

    # Se o bot recebeu carta_ids no corpo da requisição, usa elas, senão escolhe aleatórias
    if dados.carta_ids:
        cartas_para_montar = dados.carta_ids
    else:
        cartas_para_montar = [c['id'] for c in random.sample(todas_cartas, min(tamanho_deck, len(todas_cartas)))]

    # Limpa o deck atual do bot
    cursor.execute("DELETE FROM deck WHERE jogador_id = %s", (dados.jogador_id,))

    # Insere as cartas
    for carta_id in cartas_para_montar:
        cursor.execute(
            "INSERT INTO deck (jogador_id, carta_id) VALUES (%s, %s)",
            (dados.jogador_id, carta_id)
        )
    db.commit()
    cursor.close()
    db.close()

    return {"msg": "Deck do bot montado com sucesso", "cartas": cartas_para_montar}

