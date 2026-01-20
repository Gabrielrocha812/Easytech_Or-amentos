from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
import os
from database import get_db
from models import Orcamento, Cliente, ItemOrcamento, StatusOrcamento, Transacao


router = APIRouter(tags=["Orçamentos"])


APP_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(APP_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# Dashboard na raiz
@router.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    orcamentos = db.query(Orcamento).order_by(Orcamento.criado_em.desc()).all()
    total_abertos = db.query(func.count(Orcamento.id)).filter(Orcamento.status == StatusOrcamento.Aberto).scalar()
    total_fechados = db.query(func.count(Orcamento.id)).filter(Orcamento.status == StatusOrcamento.Fechado).scalar()
    total_cancelados = db.query(func.count(Orcamento.id)).filter(Orcamento.status == StatusOrcamento.Cancelado).scalar()


    return templates.TemplateResponse(
    "dashboard.html",
    {"request": request, "orcamentos": orcamentos, "abertos": total_abertos or 0, "fechados": total_fechados or 0, "cancelados": total_cancelados or 0}
    )


@router.get("/orcamentos/novo")
def form_orcamento(request: Request, db: Session = Depends(get_db)):
    clientes = db.query(Cliente).order_by(Cliente.nome.asc()).all()
    return templates.TemplateResponse("novo_orcamento.html", {"request": request, "clientes": clientes})


@router.post("/orcamentos/novo")
def criar_orcamento(cliente_id: int = Form(...), descricao: str = Form(...), valor_total: float = Form(...), db: Session = Depends(get_db)):
    orc = Orcamento(cliente_id=cliente_id, descricao=descricao, valor_total=valor_total)
    db.add(orc)
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@router.post("/orcamentos/{orcamento_id}/status")
def atualizar_status(orcamento_id: int, status: str = Form(...), db: Session = Depends(get_db)):
    orc = db.query(Orcamento).get(orcamento_id)
    if orc:
        orc.status = StatusOrcamento[status]
        db.commit()
    if status == "Fechado":
        entrada = Transacao(tipo="Entrada", descricao=f"Orçamento #{orcamento_id}", valor=orc.valor_total)
        db.add(entrada)
        db.commit()
    return RedirectResponse(url="/", status_code=303)