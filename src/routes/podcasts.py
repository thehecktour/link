from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.models.podcast import Podcast
from src.services.spotify_service import obter_token_acesso, obter_top_podcasts

router = APIRouter(prefix="/api/v1", tags=["Podcasts"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/obter_top_podcasts")
def atualizar_podcasts(db: Session = Depends(get_db)):
    token = obter_token_acesso()
    podcasts = obter_top_podcasts(token=token)

    db.query(Podcast).delete()
    db.commit()

    for show in podcasts:
        novo_podcast = Podcast(
            id=show['id'],
            titulo=show['name'],
            descricao=show['description'],
            publicador=show['publisher'],
            url=show['external_urls']['spotify'],
            imagem_url=show['images'][0]['url'] if show['images'] else None,
            categorias="negócios"
        )
        db.add(novo_podcast)
    db.commit()

    return {"mensagem": f"{len(podcasts)} podcasts atualizados e salvos no banco de dados."}

@router.get("/conteudo-lbs")
def obter_conteudo_lbs(db: Session = Depends(get_db)):
    podcasts = db.query(Podcast).all()
    conteudo = {
        "podcasts": [
            {
                "id": p.id,
                "tipo": "podcast",
                "titulo": p.titulo,
                "descricao": p.descricao,
                "publicador": p.publicador,
                "url": p.url,
                "imagem_url": p.imagem_url,
                "categorias": [p.categorias]
            } for p in podcasts
        ],
        "livros": [],
        "aulas": []
    }
    return {
        "totalItens": len(podcasts),
        "conteudo": conteudo
    }
