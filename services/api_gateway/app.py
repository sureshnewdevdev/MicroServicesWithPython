"""FastAPI application acting as a simple API Gateway."""

import os
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Request, Response


def create_app() -> FastAPI:
    """Create and configure the API gateway application."""
    app = FastAPI(title="API Gateway", version="1.0.0")

    # Base URLs for downstream services, overridable via environment variables.
    user_service_url = os.getenv("USER_SERVICE_URL", "http://localhost:8000")
    order_service_url = os.getenv("ORDER_SERVICE_URL", "http://localhost:8001")

    @app.on_event("startup")
    async def startup_event() -> None:
        """Initialize shared HTTP client when the service starts."""
        app.state.client = httpx.AsyncClient()

    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        """Close the shared HTTP client during shutdown."""
        await app.state.client.aclose()

    async def forward_request(
        method: str,
        base_url: str,
        path: str,
        request: Request,
        json: Optional[dict] = None,
    ) -> Response:
        """Forward an incoming request to a downstream service and return its response."""
        url = f"{base_url}{path}"
        try:
            response = await app.state.client.request(method, url, json=json)
        except httpx.RequestError as exc:
            # Provide a clear upstream error message to the client while preserving context.
            raise HTTPException(status_code=503, detail=f"Upstream request failed: {exc}") from exc

        return Response(
            content=response.content,
            status_code=response.status_code,
            media_type=response.headers.get("content-type"),
        )

    @app.get("/health")
    async def health() -> dict:
        """Lightweight health check endpoint."""
        return {"status": "ok"}

    @app.get("/users")
    async def list_users(request: Request) -> Response:
        """Fetch the list of users from the user service."""
        return await forward_request("GET", user_service_url, "/users", request)

    @app.post("/users")
    async def create_user(request: Request) -> Response:
        """Create a new user by forwarding the payload to the user service."""
        body = await request.json()
        return await forward_request("POST", user_service_url, "/users", request, json=body)

    @app.get("/users/{user_id}")
    async def get_user(user_id: int, request: Request) -> Response:
        """Retrieve a single user from the user service."""
        return await forward_request("GET", user_service_url, f"/users/{user_id}", request)

    @app.get("/orders")
    async def list_orders(request: Request) -> Response:
        """Fetch the list of orders from the order service."""
        return await forward_request("GET", order_service_url, "/orders", request)

    @app.post("/orders")
    async def create_order(request: Request) -> Response:
        """Create a new order via the order service."""
        body = await request.json()
        return await forward_request("POST", order_service_url, "/orders", request, json=body)

    @app.get("/orders/{order_id}")
    async def get_order(order_id: int, request: Request) -> Response:
        """Retrieve a single order from the order service."""
        return await forward_request("GET", order_service_url, f"/orders/{order_id}", request)

    return app


# Application instance used by ASGI servers (e.g., uvicorn, gunicorn).
app = create_app()
