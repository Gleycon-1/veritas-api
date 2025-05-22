from src.db.database import engine
from src.db.models import Base

# Cria todas as tabelas definidas nos modelos ORM
Base.metadata.create_all(bind=engine)

print("✅ Tabelas criadas com sucesso.")
