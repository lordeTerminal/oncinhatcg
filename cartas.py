from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_db

router = APIRouter()

# -----------------------------
# Modelo de entrada para adição/remoção
# -----------------------------
class DeckOperacao(BaseModel):
    jogador_id: int
    carta_id: int

# -----------------------------
# Listar todas as cartas do jogo
# -----------------------------
@router.get("/cartas")
def listar_cartas():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, nome, ataque, hp, mana, efeitos, descricao, imagem 
        FROM carta
    """)
    cartas = cursor.fetchall()

    cursor.close()
    db.close()
    return cartas

# -----------------------------
# Listar apenas os IDs das cartas do deck de um jogador
# -----------------------------
@router.get("/deck/{jogador_id}")
def listar_ids_cartas_do_deck(jogador_id: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT carta_id FROM deck WHERE jogador_id=%s", (jogador_id,))
    cartas = cursor.fetchall()

    cursor.close()
    db.close()
    return [carta["carta_id"] for carta in cartas]

# -----------------------------
# Adicionar carta ao deck
# -----------------------------
@router.post("/deck/adicionar")
def adicionar_carta_no_deck(dados: DeckOperacao):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id FROM deck WHERE jogador_id=%s AND carta_id=%s",
                   (dados.jogador_id, dados.carta_id))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Carta já está no deck")

    cursor.execute("INSERT INTO deck (jogador_id, carta_id) VALUES (%s, %s)",
                   (dados.jogador_id, dados.carta_id))

    db.commit()
    cursor.close()
    db.close()

    return {"msg": "Carta adicionada ao deck com sucesso"}

# -----------------------------
# Remover carta do deck
# -----------------------------
@router.post("/deck/remover")
def remover_carta_do_deck(dados: DeckOperacao):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("DELETE FROM deck WHERE jogador_id=%s AND carta_id=%s",
                   (dados.jogador_id, dados.carta_id))

    db.commit()
    cursor.close()
    db.close()

    return {"msg": "Carta removida do deck com sucesso"}

# -----------------------------
# Listar detalhes completos das cartas do deck de um jogador
# -----------------------------
@router.get("/deck/cartas/{jogador_id}")
def listar_cartas_do_deck_completas(jogador_id: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.id, c.nome, c.ataque, c.hp, c.mana, c.efeitos, c.descricao, c.imagem
        FROM deck d
        JOIN carta c ON d.carta_id = c.id
        WHERE d.jogador_id = %s
    """, (jogador_id,))

    cartas = cursor.fetchall()
    cursor.close()
    db.close()
    return cartas

