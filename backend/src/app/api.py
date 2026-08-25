from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1", tags=["control-plane"])


class ClientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)


class Client(BaseModel):
    client_id: UUID
    name: str
    status: str = "active"


class FilmCreate(BaseModel):
    client_id: UUID
    name: str = Field(min_length=1, max_length=200)
    source_language: str = Field(min_length=2, max_length=20)
    target_languages: list[str] = Field(default_factory=list)


class Film(BaseModel):
    film_id: UUID
    client_id: UUID
    name: str
    source_language: str
    target_languages: list[str]
    status: str = "draft"


_clients: dict[UUID, Client] = {}
_films: dict[UUID, Film] = {}


@router.post("/clients", response_model=Client, status_code=status.HTTP_201_CREATED)
def create_client(payload: ClientCreate) -> Client:
    client = Client(client_id=uuid4(), name=payload.name)
    _clients[client.client_id] = client
    return client


@router.get("/clients/{client_id}", response_model=Client)
def get_client(client_id: UUID) -> Client:
    client = _clients.get(client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.post("/films", response_model=Film, status_code=status.HTTP_201_CREATED)
def create_film(payload: FilmCreate) -> Film:
    if payload.client_id not in _clients:
        raise HTTPException(status_code=404, detail="Client not found")

    film = Film(
        film_id=uuid4(),
        client_id=payload.client_id,
        name=payload.name,
        source_language=payload.source_language,
        target_languages=payload.target_languages,
    )
    _films[film.film_id] = film
    return film


@router.get("/films/{film_id}", response_model=Film)
def get_film(film_id: UUID) -> Film:
    film = _films.get(film_id)
    if film is None:
        raise HTTPException(status_code=404, detail="Film not found")
    return film
