"""FastAPI application that manages in-memory user data."""

from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class User(BaseModel):
    """Representation of a stored user."""

    id: int
    name: str
    email: str


class CreateUser(BaseModel):
    """Payload for creating a new user."""

    name: str
    email: str


def create_app() -> FastAPI:
    """Create the user service application and register routes."""
    app = FastAPI(title="User Service", version="1.0.0")
    # In-memory store for user records; not intended for production use.
    users: List[User] = []

    @app.get("/health")
    async def health() -> dict:
        """Health probe endpoint."""
        return {"status": "ok"}

    @app.get("/users", response_model=List[User])
    async def list_users() -> List[User]:
        """Return all users currently stored in memory."""
        return users

    @app.post("/users", response_model=User, status_code=201)
    async def add_user(payload: CreateUser) -> User:
        """Add a new user to the in-memory list."""
        next_id = len(users) + 1
        user = User(id=next_id, **payload.dict())
        users.append(user)
        return user

    @app.get("/users/{user_id}", response_model=User)
    async def get_user(user_id: int) -> User:
        """Retrieve a user by ID or raise a 404 if missing."""
        for user in users:
            if user.id == user_id:
                return user
        raise HTTPException(status_code=404, detail="User not found")

    return app


# Application instance used by ASGI servers.
app = create_app()

