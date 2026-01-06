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
    return templates.TemplateResponse("index.html", {"request": request, "datetime": datetime })


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
    observacoes: str = Form("")
):
    # Caminho do logotipo
    logo_path = os.path.join(STATIC_DIR, "logo.png").replace("\\", "/")

    # Renderizar HTML com variáveis
    html_content = env.get_template("nota_recebimento.html").render({
        "logo_path": f"file:///{logo_path}",
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
        "observacoes": observacoes.strip()
    })

    # Gerar PDF
    pdf_bytes = HTML(string=html_content, base_url=BASE_DIR).write_pdf()

    # Nome limpo e seguro
    nome_arquivo = f"Nota_Recebimento_{cliente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

    # Retornar como download
    return Response(
        pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nome_arquivo}"'}
    )
# ==========================================================
#   GERAÇÃO DE PDF — ORDEM DE SERVIÇO
# ==========================================================

@app.post("/gerar-ordem-servico")
async def gerar_ordem_servico(
    numero_os: str = Form(...),
    data_abertura: str = Form(...),
    cliente: str = Form(...),
    endereco: str = Form(...),
    data_execucao: str = Form(...),
    tecnico: str = Form(...),
    descricao_servico: str = Form(...)
):
    logo_path = os.path.join(STATIC_DIR, "logo.png").replace("\\", "/")

    html_content = env.get_template("ordem_servico.html").render({
        "logo_path": f"file:///{logo_path}",
        "numero_os": numero_os,
        "data_abertura": data_abertura,
        "cliente": cliente,
        "endereco": endereco,
        "data_execucao": data_execucao,
        "tecnico": tecnico,
        "descricao_servico": descricao_servico,
    })

    pdf_bytes = HTML(string=html_content, base_url=BASE_DIR).write_pdf()
    nome_arquivo = f"OS_{numero_os}_{cliente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"

    return Response(
        pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nome_arquivo}"'}
    )

@app.get("/site", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("site.html", {"request": request})

@app.get("/vale", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("vale.html", {"request": request})

@app.get("/core", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("core/index.html", {"request": request})