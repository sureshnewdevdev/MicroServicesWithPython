from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class Order(BaseModel):
    id: int
    user_id: int
    item: str
    quantity: int


class CreateOrder(BaseModel):
    user_id: int
    item: str
    quantity: int


def create_app() -> FastAPI:
    app = FastAPI(title="Order Service", version="1.0.0")
    orders: List[Order] = []

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    @app.get("/orders", response_model=List[Order])
    async def list_orders() -> List[Order]:
        return orders

    @app.post("/orders", response_model=Order, status_code=201)
    async def create_order(payload: CreateOrder) -> Order:
        if payload.quantity <= 0:
            raise HTTPException(status_code=422, detail="Quantity must be positive")

        next_id = len(orders) + 1
        order = Order(id=next_id, **payload.dict())
        orders.append(order)
        return order

    @app.get("/orders/{order_id}", response_model=Order)
    async def get_order(order_id: int) -> Order:
        for order in orders:
            if order.id == order_id:
                return order
        raise HTTPException(status_code=404, detail="Order not found")

    return app


app = create_app()

