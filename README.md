# Python Microservices (no Docker)

This repository contains two FastAPI-based microservices and an API Gateway that can be run locally without Docker.

## Services

- **User Service** (`services/user_service/app.py`): manage a list of users.
- **Order Service** (`services/order_service/app.py`): manage orders tied to a `user_id`.
- **API Gateway** (`services/api_gateway/app.py`): forwards requests to the User and Order services.

Both services keep data in-memory for simplicity.

## Getting started

1. Create and activate a virtual environment (example using `venv`):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the services

Start each service in its own shell session. Neither service uses Docker.

```bash
# User service on port 8000
uvicorn services.user_service.app:app --reload --port 8000

# Order service on port 8001
uvicorn services.order_service.app:app --reload --port 8001

# API Gateway on port 8002
uvicorn services.api_gateway.app:app --reload --port 8002
```

### Health checks
- User service: `http://localhost:8000/health`
- Order service: `http://localhost:8001/health`
- API Gateway: `http://localhost:8002/health`

### Example requests
Create a user (via the gateway):
```bash
curl -X POST http://localhost:8002/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Ada Lovelace", "email": "ada@example.com"}'
```

Create an order (via the gateway):
```bash
curl -X POST http://localhost:8002/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "item": "Notebook", "quantity": 2}'
```

List data:
```bash
curl http://localhost:8002/users
curl http://localhost:8002/orders
```

## Notes
- Data resets when a service restarts (in-memory storage).
- The services are intentionally lightweight to run without containers.
- You can point the gateway at different upstream URLs by setting `USER_SERVICE_URL` and `ORDER_SERVICE_URL` environment variables before starting it.
