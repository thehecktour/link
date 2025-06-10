from sqlalchemy import Column, String, Text
from src.core.database import Base

class Podcast(Base):
    __tablename__ = "podcasts"

    id = Column(String, primary_key=True, index=True)
    titulo = Column(String)
    descricao = Column(Text)
    publicador = Column(String)
    url = Column(String)
    imagem_url = Column(String)
    categorias = Column(String)
