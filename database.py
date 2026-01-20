from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv


# Carrega variáveis do .env na raiz do projeto
load_dotenv()


# Exemplo de fallback local; prefira definir no .env
DATABASE_URL = os.getenv("DATABASE_URL")


# Parâmetros úteis de conexão/robustez
ENGINE_KW = dict(
pool_pre_ping=True, # recicla conexões quebradas
pool_size=5,
max_overflow=10,
pool_recycle=1800, # 30 min
connect_args={}, # ex.: {"sslmode": "require"} se precisar
)


engine = create_engine(DATABASE_URL, **ENGINE_KW)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


# Dependency (sessão por request)
from contextlib import contextmanager
from typing import Generator


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()