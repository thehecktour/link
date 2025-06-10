from fastapi import APIRouter, Depends, HTTPException
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

def inserir_podcasts(db: Session, lista_podcasts: list, pais: str):
    for show in lista_podcasts:
        podcast_existente = db.query(Podcast).filter(Podcast.id == show['id']).first()
        if podcast_existente:
            podcast_existente.titulo = show['name']
            podcast_existente.descricao = show['description']
            podcast_existente.publicador = show['publisher']
            podcast_existente.url = show['external_urls']['spotify']
            podcast_existente.imagem_url = show['images'][0]['url'] if show['images'] else None
            podcast_existente.categorias = "negócios"
            podcast_existente.pais = pais
        else:
            novo_podcast = Podcast(
                id=show['id'],
                titulo=show['name'],
                descricao=show['description'],
                publicador=show['publisher'],
                url=show['external_urls']['spotify'],
                imagem_url=show['images'][0]['url'] if show['images'] else None,
                categorias="negócios",
                pais=pais
            )
            db.add(novo_podcast)
    db.commit()


@router.get("/obter_top_podcasts")
def atualizar_podcasts(db: Session = Depends(get_db)):
    token = obter_token_acesso()

    podcasts_br = obter_top_podcasts(token=token, pais='BR', limite=25)
    podcasts_us = obter_top_podcasts(token=token, pais='US', limite=25)

    db.query(Podcast).delete()
    db.commit()

    inserir_podcasts(db, podcasts_br, 'BR')
    inserir_podcasts(db, podcasts_us, 'US')

    db.commit()

    total = len(podcasts_br) + len(podcasts_us)
    return {"mensagem": f"{total} podcasts atualizados e salvos no banco de dados."}

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
                "categorias": [p.categorias],
                "pais": p.pais
            } for p in podcasts
        ],
        "livros": [],
        "aulas": []
    }
    return {
        "totalItens": len(podcasts),
        "conteudo": conteudo
    }
