import os
import random
from datetime import datetime
from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

app = FastAPI()

# --- Configuração de Diretórios e Templates ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Monta o diretório estático para acesso público (se necessário)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Configura o Jinja2 para carregar templates
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# --- Rotas da Aplicação ---
@app.get("/")
async def form_page(request: Request):
    # O form.html que suporta múltiplos produtos
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/gerar-pdf")
async def gerar_pdf(
    # --- Dados do Cabeçalho e Rodapé ---
    cliente: str = Form(...),
    contato_cliente: str = Form(...),
    emissao: str = Form(...),
    validade: str = Form(...),
    desconto: float = Form(...),
    # --- Dados dos Itens (Listas) ---
    produto: List[str] = Form(...),
    quantidade: List[int] = Form(...),
    valor_unitario: List[float] = Form(...)
):
    # --- Processamento dos Dados ---
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

    # Caminho absoluto para a imagem da logo
    logo_path = os.path.join(STATIC_DIR, "logo.png").replace("\\", "/")

    # Dados a serem passados para o template HTML
    template_data = {
        "logo_path": f"file:///{logo_path}",
        "cliente": cliente,
        "contato_cliente": contato_cliente,
        "emissao": emissao,
        "validade": validade,
        "itens": itens,
        "subtotal": subtotal,
        "desconto": desconto,
        "total_final": total_final
    }
    
    # --- Geração do PDF a partir do HTML ---
    template = env.get_template("invoice_template.html")
    html_string = template.render(template_data)

    pdf_bytes = HTML(string=html_string, base_url=BASE_DIR).write_pdf()

    # --- Resposta do Servidor ---
    nome_download = f"Orcamento_{cliente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    headers = {
        'Content-Disposition': f'attachment; filename="{nome_download}"'
    }

    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)

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

    html = env.get_template("nota_recebimento.html").render({
        "logo_path": f"file:///{logo_path}",
        "fornecedor": fornecedor,
        "cnpj": cnpj,
        "data_recebimento": data_recebimento,
        "responsavel": responsavel,
        "observacoes": observacoes,
        "itens": itens
    })

    pdf_bytes = HTML(string=html, base_url=BASE_DIR).write_pdf()
    nome_download = f"Nota_Recebimento_{fornecedor}_{datetime.now().strftime('%Y%m%d')}.pdf"
    return Response(pdf_bytes, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{nome_download}"'})


# --- Ordem de Serviço ---
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

    html = env.get_template("ordem_servico.html").render({
        "logo_path": f"file:///{logo_path}",
        "cliente": cliente,
        "endereco": endereco,
        "data_execucao": data_execucao,
        "tecnico": tecnico,
        "descricao_servico": descricao_servico,
        "itens": itens,
        "total": total
    })

    pdf_bytes = HTML(string=html, base_url=BASE_DIR).write_pdf()
    nome_download = f"Ordem_Servico_{cliente}_{datetime.now().strftime('%Y%m%d')}.pdf"
    return Response(pdf_bytes, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{nome_download}"'})