"""FastAPI application that simulates an order management service."""

from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class Order(BaseModel):
    """Representation of a stored order."""

    id: int
    user_id: int
    item: str
    quantity: int


class CreateOrder(BaseModel):
    """Payload for creating a new order."""

    user_id: int
    item: str
    quantity: int


def create_app() -> FastAPI:
    """Create the order service application and register routes."""
    app = FastAPI(title="Order Service", version="1.0.0")
    # In-memory store for order records; suitable for demos and tests only.
    orders: List[Order] = []

    @app.get("/health")
    async def health() -> dict:
        """Health probe endpoint."""
        return {"status": "ok"}

    @app.get("/orders", response_model=List[Order])
    async def list_orders() -> List[Order]:
        """Return all orders currently stored in memory."""
        return orders

    @app.post("/orders", response_model=Order, status_code=201)
    async def create_order(payload: CreateOrder) -> Order:
        """Create a new order and validate the quantity."""
        if payload.quantity <= 0:
            raise HTTPException(status_code=422, detail="Quantity must be positive")

        next_id = len(orders) + 1
        order = Order(id=next_id, **payload.dict())
        orders.append(order)
        return order

    @app.get("/orders/{order_id}", response_model=Order)
    async def get_order(order_id: int) -> Order:
        """Retrieve an order by ID or raise a 404 if missing."""
        for order in orders:
            if order.id == order_id:
                return order
        raise HTTPException(status_code=404, detail="Order not found")

    return app


# Application instance used by ASGI servers.
app = create_app()

