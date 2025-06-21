import mysql.connector

def listar_cartas(cursor):
    cursor.execute("SELECT id, nome, ataque, hp, mana FROM carta ORDER BY id")
    cartas = cursor.fetchall()
    print("\nCartas disponíveis:")
    for carta in cartas:
        print(f"{carta[0]:>2} - {carta[1]:20} | ATK: {carta[2]} | HP: {carta[3]} | Mana: {carta[4]}")
    return [c[0] for c in cartas]  # Retorna lista de ids válidos

def escolher_deck(cursor, conn, jogador_id, tamanho_deck=5):
    ids_validos = listar_cartas(cursor)
    escolhas = []
    print(f"\nEscolha {tamanho_deck} cartas para seu deck (digite o ID da carta):")

    while len(escolhas) < tamanho_deck:
        try:
            escolha = int(input(f"Carta {len(escolhas)+1}: "))
            if escolha in ids_validos and escolha not in escolhas:
                escolhas.append(escolha)
            else:
                print("ID inválido ou carta já escolhida. Tente novamente.")
        except ValueError:
            print("Por favor, digite um número válido.")

    # Apaga deck antigo e insere novo
    cursor.execute("DELETE FROM deck WHERE jogador_id = %s", (jogador_id,))
    for carta_id in escolhas:
        cursor.execute("INSERT INTO deck (jogador_id, carta_id) VALUES (%s, %s)", (jogador_id, carta_id))
    conn.commit()

    print("\nDeck atualizado com sucesso! Suas cartas escolhidas:")
    cursor.execute("""
        SELECT nome FROM carta WHERE id IN (%s)
    """ % (",".join(str(idc) for idc in escolhas)))
    for row in cursor.fetchall():
        print(f"- {row[0]}")

if __name__ == "__main__":
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="golimar10*",
        database="cards"
    )
    cursor = conn.cursor()

    jogador_id = int(input("Digite seu ID de jogador: "))
    escolher_deck(cursor, conn, jogador_id)

    cursor.close()
    conn.close()

