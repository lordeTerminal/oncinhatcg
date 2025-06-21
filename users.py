from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_db
from auth import hash_senha, verificar_senha

router = APIRouter()

class Usuario(BaseModel):
    nome: str
    email: str
    senha: str

@router.post("/registrar")
def registrar(usuario: Usuario):
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT id FROM user WHERE email = %s", (usuario.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email já registrado")
    
    senha_hash = hash_senha(usuario.senha)
    cursor.execute("INSERT INTO user (nome, email, senha) VALUES (%s, %s, %s)",
                   (usuario.nome, usuario.email, senha_hash))
    user_id = cursor.lastrowid

    # Criar jogador vinculado
    cursor.execute("INSERT INTO jogador (nome, hp, defesa, descricao, user_id) VALUES (%s, %s, %s, %s, %s)",
                   (usuario.nome, 100, 10, 'Jogador inicial', user_id))

    db.commit()
    cursor.close()
    db.close()

    return {"msg": "Usuário registrado com sucesso"}

class LoginInput(BaseModel):
    email: str
    senha: str

@router.post("/login")
def login(dados: LoginInput):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM user WHERE email = %s", (dados.email,))
    user = cursor.fetchone()
    if not user or not verificar_senha(dados.senha, user['senha']):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    # Buscar jogador vinculado
    cursor.execute("SELECT id FROM jogador WHERE user_id = %s", (user['id'],))
    jogador = cursor.fetchone()

    return {
        "msg": "Login bem-sucedido",
        "user_id": user["id"],
        "nome": user["nome"],
        "jogador_id": jogador["id"] if jogador else None
    }

