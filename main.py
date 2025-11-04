import os
from datetime import datetime
from typing import List
from fastapi import FastAPI, Form, Request
from fastapi.responses import Response, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

app = FastAPI()

# --- Diretórios base ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# --- Monta diretório estático ---
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# --- Configura Jinja2 ---
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# ==========================================================
#   PÁGINAS PRINCIPAIS
# ==========================================================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página principal com menu lateral."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/orcamento", response_class=HTMLResponse)
async def form_orcamento(request: Request):
    """Formulário de orçamento."""
    return templates.TemplateResponse("form_orcamento.html", {"request": request})


@app.get("/nota-recebimento", response_class=HTMLResponse)
async def form_nota_recebimento(request: Request):
    """Formulário de nota de recebimento."""
    return templates.TemplateResponse("form_nota_recebimento.html", {"request": request})


@app.get("/ordem-servico", response_class=HTMLResponse)
async def form_ordem_servico(request: Request):
    """Formulário de ordem de serviço."""
    return templates.TemplateResponse("form_ordem_servico.html", {"request": request})


# ==========================================================
#   GERAÇÃO DE PDF — ORÇAMENTO
# ==========================================================

@app.post("/gerar-pdf")
async def gerar_pdf(
    cliente: str = Form(...),
    contato_cliente: str = Form(...),
    emissao: str = Form(...),
    validade: str = Form(...),
    desconto: float = Form(...),
    produto: List[str] = Form(...),
    quantidade: List[int] = Form(...),
    valor_unitario: List[float] = Form(...)
):
    itens = []
    subtotal = 0

    for i in range(len(produto)):
        total_item = quantidade[i] * valor_unitario[i]
        subtotal += total_item
        itens.append({
            "produto": produto[i],
            "quantidade": quantidade[i],
            "valor_unitario": valor_unitario[i],
            "total_item": total_item
        })

    total_final = subtotal - desconto
    logo_path = os.path.join(STATIC_DIR, "logo.png").replace("\\", "/")

    html_content = env.get_template("invoice_template.html").render({
        "logo_path": f"file:///{logo_path}",
        "cliente": cliente,
        "contato_cliente": contato_cliente,
        "emissao": emissao,
        "validade": validade,
        "itens": itens,
        "subtotal": subtotal,
        "desconto": desconto,
        "total_final": total_final
    })

    pdf_bytes = HTML(string=html_content, base_url=BASE_DIR).write_pdf()
    nome_arquivo = f"Orcamento_{cliente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"

    return Response(pdf_bytes, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{nome_arquivo}"'})


# ==========================================================
#   GERAÇÃO DE PDF — NOTA DE RECEBIMENTO
# ==========================================================

@app.post("/gerar-nota-recebimento")
async def gerar_nota_recebimento(
    fornecedor: str = Form(...),
    cnpj: str = Form(...),
    data_recebimento: str = Form(...),
    responsavel: str = Form(...),
    observacoes: str = Form(""),
    produto: List[str] = Form(...),
    quantidade: List[int] = Form(...)
):
    itens = [{"produto": p, "quantidade": q} for p, q in zip(produto, quantidade)]
    logo_path = os.path.join(STATIC_DIR, "logo.png").replace("\\", "/")

    html_content = env.get_template("nota_recebimento.html").render({
        "logo_path": f"file:///{logo_path}",
        "fornecedor": fornecedor,
        "cnpj": cnpj,
        "data_recebimento": data_recebimento,
        "responsavel": responsavel,
        "observacoes": observacoes,
        "itens": itens
    })

    pdf_bytes = HTML(string=html_content, base_url=BASE_DIR).write_pdf()
    nome_arquivo = f"Nota_Recebimento_{fornecedor.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"

    return Response(pdf_bytes, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{nome_arquivo}"'})


# ==========================================================
#   GERAÇÃO DE PDF — ORDEM DE SERVIÇO
# ==========================================================

@app.post("/gerar-ordem-servico")
async def gerar_ordem_servico(
    cliente: str = Form(...),
    endereco: str = Form(...),
    data_execucao: str = Form(...),
    tecnico: str = Form(...),
    descricao_servico: str = Form(...),
    materiais_usados: List[str] = Form(...),
    valores: List[float] = Form(...)
):
    itens = [{"material": m, "valor": v} for m, v in zip(materiais_usados, valores)]
    total = sum(valores)
    logo_path = os.path.join(STATIC_DIR, "logo.png").replace("\\", "/")

    html_content = env.get_template("ordem_servico.html").render({
        "logo_path": f"file:///{logo_path}",
        "cliente": cliente,
        "endereco": endereco,
        "data_execucao": data_execucao,
        "tecnico": tecnico,
        "descricao_servico": descricao_servico,
        "itens": itens,
        "total": total
    })

    pdf_bytes = HTML(string=html_content, base_url=BASE_DIR).write_pdf()
    nome_arquivo = f"Ordem_Servico_{cliente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"

    return Response(pdf_bytes, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{nome_arquivo}"'})
