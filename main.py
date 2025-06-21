from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # <-- importa isso
from routes import users, deck, cartas, batalha

app = FastAPI()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restrinja isso!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos (como imagens)
app.mount("/images", StaticFiles(directory="static/images"), name="images")  # <-- monta os arquivos

# Rotas da API
app.include_router(users.router, prefix="/api", tags=["Usuários"])
app.include_router(batalha.router, prefix="/api", tags=["Batalha"])
app.include_router(deck.router, prefix="/api", tags=["Deck"])
app.include_router(cartas.router, prefix="/api", tags=["Cartas"])

@app.get("/")
def root():
    return {"msg": "API do Tiger Mage está ativa"}

