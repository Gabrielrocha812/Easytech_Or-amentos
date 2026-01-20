import os
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session
from weasyprint import HTML

from database import get_db
from models import Orcamento, Cliente

router = APIRouter(prefix="/documentos", tags=["Documentos"])

APP_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(APP_DIR, "templates", "documentos")
STATIC_DIR = os.path.join(APP_DIR, "static", "documentos")

# Jinja para páginas HTML (preview/form)
templates = Jinja2Templates(directory=os.path.join(APP_DIR, "templates"))

# Jinja dedicado aos templates de PDF
pdf_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


def _logo_file_uri() -> str:
    logo_path = os.path.join(STATIC_DIR, "logo.png").replace("\\", "/")
    return f"file:///{logo_path}"


# -------------------------------
# Orçamento (integrado ao ERP)
# -------------------------------

@router.get("/orcamento/{orcamento_id}", response_class=HTMLResponse)
def preview_orcamento(request: Request, orcamento_id: int, db: Session = Depends(get_db)):
    orc = db.query(Orcamento).get(orcamento_id)
    if not orc:
        return HTMLResponse("Orçamento não encontrado.", status_code=404)

    cliente = db.query(Cliente).get(orc.cliente_id) if orc.cliente_id else None

    # Página simples de preview/ações (sem template novo: render inline)
    html = f"""
    <html lang='pt-br'>
    <head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
    <title>Orçamento #{orc.id}</title></head>
    <body style='font-family: Arial, sans-serif; padding: 24px;'>
      <h2>Orçamento #{orc.id}</h2>
      <p><b>Cliente:</b> {cliente.nome if cliente else '-'} </p>
      <p><b>Descrição:</b><br>{(orc.descricao or '').replace(chr(10), '<br>')}</p>
      <p><b>Valor total:</b> R$ {orc.valor_total or 0:.2f}</p>
      <p><a href='/documentos/orcamento/{orc.id}/pdf'>Baixar PDF</a> | <a href='/'>Voltar</a></p>
    </body>
    </html>
    """
    return HTMLResponse(html)


@router.get("/orcamento/{orcamento_id}/pdf")
def baixar_pdf_orcamento(orcamento_id: int, db: Session = Depends(get_db)):
    orc = db.query(Orcamento).get(orcamento_id)
    if not orc:
        return HTMLResponse("Orçamento não encontrado.", status_code=404)

    cliente = db.query(Cliente).get(orc.cliente_id) if orc.cliente_id else None

    # Como o módulo atual não possui itens detalhados, geramos 1 item com a descrição
    itens = [{
        "produto": (orc.descricao or "Serviço/Produto"),
        "quantidade": 1,
        "valor_unitario": float(orc.valor_total or 0),
        "total_item": float(orc.valor_total or 0),
    }]

    subtotal = float(orc.valor_total or 0)
    desconto = 0.0
    total_final = subtotal

    emissao = (orc.criado_em.strftime("%d/%m/%Y") if getattr(orc, "criado_em", None) else datetime.now().strftime("%d/%m/%Y"))

    html_content = pdf_env.get_template("invoice_template.html").render({
        "logo_path": _logo_file_uri(),
        "cliente": (cliente.nome if cliente else "Cliente"),
        "contato_cliente": (cliente.telefone if cliente else ""),
        "emissao": emissao,
        "validade": "7 dias",
        "itens": itens,
        "subtotal": subtotal,
        "desconto": desconto,
        "total_final": total_final,
    })

    pdf_bytes = HTML(string=html_content, base_url=APP_DIR).write_pdf()
    nome_arquivo = f"Orcamento_{orcamento_id}_{datetime.now().strftime('%Y%m%d')}.pdf"

    return Response(
        pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nome_arquivo}"'},
    )


# -------------------------------
# Nota de recebimento (form + PDF)
# -------------------------------

@router.get("/nota-recebimento", response_class=HTMLResponse)
def form_nota(request: Request):
    return templates.TemplateResponse("documentos/form_nota_recebimento.html", {"request": request})


@router.post("/nota-recebimento/pdf")
def gerar_nota_recebimento(
    cliente: str = Form(...),
    contato_cliente: str = Form(...),
    cpf_cnpj: str = Form(""),
    telefone: str = Form(""),
    data_recebimento: str = Form(...),
    responsavel: str = Form(...),
    numero_registro: str = Form(...),
    tipo_equipamento: str = Form(...),
    marca_modelo: str = Form(...),
    numero_serie: str = Form(""),
    acessorios: str = Form(""),
    condicao: str = Form(""),
    observacoes: str = Form(""),
):
    html_content = pdf_env.get_template("nota_recebimento.html").render({
        "logo_path": _logo_file_uri(),
        "cliente": cliente.strip(),
        "contato_cliente": contato_cliente.strip(),
        "cpf_cnpj": cpf_cnpj.strip(),
        "telefone": telefone.strip(),
        "data_recebimento": data_recebimento,
        "responsavel": responsavel.strip(),
        "numero_registro": numero_registro.strip(),
        "tipo_equipamento": tipo_equipamento.strip(),
        "marca_modelo": marca_modelo.strip(),
        "numero_serie": numero_serie.strip(),
        "acessorios": acessorios.strip(),
        "condicao": condicao.strip(),
        "observacoes": observacoes.strip(),
    })

    pdf_bytes = HTML(string=html_content, base_url=APP_DIR).write_pdf()
    nome_arquivo = f"Nota_Recebimento_{cliente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

    return Response(
        pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nome_arquivo}"'},
    )


# -------------------------------
# Ordem de serviço (form + PDF)
# -------------------------------

@router.get("/ordem-servico", response_class=HTMLResponse)
def form_os(request: Request):
    return templates.TemplateResponse("documentos/form_ordem_servico.html", {"request": request})


@router.post("/ordem-servico/pdf")
def gerar_ordem_servico(
    numero_os: str = Form(...),
    data_abertura: str = Form(...),
    cliente: str = Form(...),
    endereco: str = Form(...),
    data_execucao: str = Form(...),
    tecnico: str = Form(...),
    descricao_servico: str = Form(...),
):
    html_content = pdf_env.get_template("ordem_servico.html").render({
        "logo_path": _logo_file_uri(),
        "numero_os": numero_os,
        "data_abertura": data_abertura,
        "cliente": cliente,
        "endereco": endereco,
        "data_execucao": data_execucao,
        "tecnico": tecnico,
        "descricao_servico": descricao_servico,
    })

    pdf_bytes = HTML(string=html_content, base_url=APP_DIR).write_pdf()
    nome_arquivo = f"OS_{numero_os}_{cliente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"

    return Response(
        pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nome_arquivo}"'},
    )
