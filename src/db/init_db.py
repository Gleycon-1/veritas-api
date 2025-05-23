# src/db/init_db.py

import sys
import os

# Adiciona o diretório pai (raiz do projeto) ao sys.path
# Isso permite que importações como 'from src.db.models import ...' funcionem
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base, AnalysisModel # Importe todos os modelos que você quer criar aqui
from src.core.config import settings # Para pegar a DATABASE_URL

def init_db():
    """
    Inicializa o banco de dados, criando todas as tabelas definidas nos modelos.
    """
    # Acessa a URL do banco de dados das suas configurações
    engine = create_engine(settings.DATABASE_URL)

    # Cria todas as tabelas (Base.metadata.create_all)
    # Isso procura por todas as classes que herdam de Base e as cria como tabelas.
    Base.metadata.create_all(bind=engine)
    print(f"Tabelas do banco de dados criadas (ou já existentes) com sucesso no: {settings.DATABASE_URL}")

if __name__ == "__main__":
    # Este bloco permite que você execute 'python src/db/init_db.py' diretamente
    # para criar as tabelas.
    init_db()