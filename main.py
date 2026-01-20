# ==========================================
# Easytech Manager - Estrutura modular (FastAPI + PostgreSQL)
# ==========================================
# Main limpa com imports e inicialização
# ==========================================

import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import engine
from models import Base
from routes import clientes, documentos, financeiro, orcamentos


# Garante que as tabelas existam (em produção, ideal usar Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Easytech Manager")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


app.include_router(clientes.router)
app.include_router(orcamentos.router)
app.include_router(financeiro.router)
app.include_router(documentos.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


