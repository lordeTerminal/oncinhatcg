from fastapi import APIRouter, HTTPException
from database import get_db

router = APIRouter()

@router.get("/deck/{jogador_id}")
def obter_deck(jogador_id: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.nome, c.ataque, c.hp, c.mana, c.efeitos, c.descricao
        FROM deck d
        JOIN carta c ON d.carta_id = c.id
        WHERE d.jogador_id = %s
    """, (jogador_id,))

    cartas = cursor.fetchall()
    cursor.close()
    db.close()

    if not cartas:
        raise HTTPException(status_code=404, detail="Deck vazio ou jogador inexistente")

    return cartas

