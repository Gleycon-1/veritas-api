from src.db.database import engine
from src.db.models import Base

# Cria as tabelas no banco
Base.metadata.create_all(bind=engine)
