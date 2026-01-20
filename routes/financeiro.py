from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
import os


from database import get_db
from models import Transacao


router = APIRouter(prefix="/financeiro", tags=["Financeiro"])


APP_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(APP_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("")
def financeiro(request: Request, db: Session = Depends(get_db)):
    entradas = db.query(Transacao).filter_by(tipo="Entrada").all()
    saidas = db.query(Transacao).filter_by(tipo="Saída").all()
    total_entradas = sum(t.valor for t in entradas)
    total_saidas = sum(t.valor for t in saidas)
    saldo = total_entradas - total_saidas
    return templates.TemplateResponse("financeiro.html", {
    "request": request,
    "entradas": entradas,
    "saidas": saidas,
    "saldo": saldo
    })


@router.post("/saida/nova")
def nova_saida(descricao: str = Form(...), valor: float = Form(...), db: Session = Depends(get_db)):
    db.add(Transacao(tipo="Saída", descricao=descricao, valor=valor))
    db.commit()
    return RedirectResponse(url="/financeiro", status_code=303)