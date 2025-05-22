# src/create_tables.py

from db.database import engine, Base
from db import models

# Cria as tabelas definidas nos models
Base.metadata.create_all(bind=engine)

print("Tabelas criadas com sucesso.")
