from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os


from database import get_db
from models import Cliente


router = APIRouter(prefix="/clientes", tags=["Clientes"])


APP_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(APP_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("")
def listar(request: Request, db: Session = Depends(get_db)):
    clientes = db.query(Cliente).all()
    return templates.TemplateResponse("clientes.html", {"request": request, "clientes": clientes})


@router.post("/novo")
def novo(nome: str = Form(...), telefone: str = Form(None), email: str = Form(None), endereco: str = Form(None), db: Session = Depends(get_db)):
    db.add(Cliente(nome=nome, telefone=telefone, email=email, endereco=endereco))
    db.commit()
    return RedirectResponse(url="/clientes", status_code=303)