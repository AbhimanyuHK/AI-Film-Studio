from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.auth import Principal, get_principal
from app.repository import InMemoryRepository

router = APIRouter(prefix="/api/v1", tags=["control-plane"])
repository = InMemoryRepository()


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


def _authorize_client(principal: Principal, client_id: UUID) -> None:
    if principal.role == "platform_admin":
        return
    if principal.client_id != str(client_id):
        raise HTTPException(status_code=403, detail="Cross-client access denied")


@router.post("/clients", response_model=Client, status_code=status.HTTP_201_CREATED)
def create_client(payload: ClientCreate, _: Principal = Depends(get_principal)) -> Client:
    record = repository.create_client(payload.name)
    return Client(client_id=record.client_id, name=record.name, status=record.status)


@router.get("/clients/{client_id}", response_model=Client)
def get_client(client_id: UUID, principal: Principal = Depends(get_principal)) -> Client:
    _authorize_client(principal, client_id)
    record = repository.get_client(client_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return Client(client_id=record.client_id, name=record.name, status=record.status)


@router.post("/films", response_model=Film, status_code=status.HTTP_201_CREATED)
def create_film(payload: FilmCreate, principal: Principal = Depends(get_principal)) -> Film:
    _authorize_client(principal, payload.client_id)
    if repository.get_client(payload.client_id) is None:
        raise HTTPException(status_code=404, detail="Client not found")
    record = repository.create_film(
        payload.client_id,
        payload.name,
        payload.source_language,
        payload.target_languages,
    )
    return Film(
        film_id=record.film_id,
        client_id=record.client_id,
        name=record.name,
        source_language=record.source_language,
        target_languages=list(record.target_languages),
        status=record.status,
    )


@router.get("/films/{film_id}", response_model=Film)
def get_film(film_id: UUID, principal: Principal = Depends(get_principal)) -> Film:
    record = repository.get_film(film_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Film not found")
    _authorize_client(principal, record.client_id)
    return Film(
        film_id=record.film_id,
        client_id=record.client_id,
        name=record.name,
        source_language=record.source_language,
        target_languages=list(record.target_languages),
        status=record.status,
    )
