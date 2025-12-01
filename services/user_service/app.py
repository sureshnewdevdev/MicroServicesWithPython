from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    email: str


class CreateUser(BaseModel):
    name: str
    email: str


def create_app() -> FastAPI:
    app = FastAPI(title="User Service", version="1.0.0")
    users: List[User] = []

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    @app.get("/users", response_model=List[User])
    async def list_users() -> List[User]:
        return users

    @app.post("/users", response_model=User, status_code=201)
    async def add_user(payload: CreateUser) -> User:
        next_id = len(users) + 1
        user = User(id=next_id, **payload.dict())
        users.append(user)
        return user

    @app.get("/users/{user_id}", response_model=User)
    async def get_user(user_id: int) -> User:
        for user in users:
            if user.id == user_id:
                return user
        raise HTTPException(status_code=404, detail="User not found")

    return app


app = create_app()

