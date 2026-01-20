from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from database import Base


# ============================
# Enum para status de orçamentos
# ============================
class StatusOrcamento(enum.Enum):
    Aberto = "Aberto"
    Fechado = "Fechado"
    Cancelado = "Cancelado"


# ============================
# Modelo de Cliente
# ============================
class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    telefone = Column(String)
    email = Column(String)
    endereco = Column(String)
    criado_em = Column(DateTime, default=datetime.now)

    # Relacionamento com Orcamentos
    orcamentos = relationship(
        "Orcamento",
        back_populates="cliente",
        cascade="all, delete-orphan"
    )


# ============================
# Modelo de Orçamento
# ============================
class Orcamento(Base):
    __tablename__ = "orcamentos"

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    descricao = Column(String)
    valor_total = Column(Float)
    status = Column(Enum(StatusOrcamento), default=StatusOrcamento.Aberto)
    criado_em = Column(DateTime, default=datetime.now)
    atualizado_em = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relacionamentos
    cliente = relationship("Cliente", back_populates="orcamentos")
    itens = relationship(
        "ItemOrcamento",
        back_populates="orcamento",
        cascade="all, delete-orphan"
    )


# ============================
# Modelo de Itens de Orçamento
# ============================
class ItemOrcamento(Base):
    __tablename__ = "itens_orcamento"

    id = Column(Integer, primary_key=True)
    orcamento_id = Column(Integer, ForeignKey("orcamentos.id"))
    produto = Column(String)
    quantidade = Column(Integer)
    preco_unitario = Column(Float)
    subtotal = Column(Float)

    # Relacionamento com Orcamento
    orcamento = relationship("Orcamento", back_populates="itens")


# ============================
# Modelo de Transação Financeira
# ============================
class Transacao(Base):
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True)
    tipo = Column(String)  # Entrada ou Saída
    descricao = Column(String)
    valor = Column(Float)
    data = Column(DateTime, default=datetime.now)
