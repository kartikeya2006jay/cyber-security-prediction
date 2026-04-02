# Secure Authentication + RBAC Setup

## 1) Backend Setup (FastAPI)

1. Open terminal in project root.
2. Create and activate a virtual environment.
3. Install backend dependencies:

```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and fill secure values.
5. Run backend API:

```bash
uvicorn app.main:app --reload --app-dir backend
```

Backend runs at `http://localhost:8000`.

## 2) Frontend Setup (React + Vite)

1. Open terminal in `frontend`.
2. Install dependencies:

```bash
npm install
```

3. Copy `frontend/.env.example` to `frontend/.env`.
4. Start frontend:

```bash
npm run dev
```

Frontend runs at `http://localhost:5173`.

## 3) API Endpoints

- `POST /auth/login` (rate-limited, logs attempts)
- `POST /auth/create-user` (SUPER_ADMIN only)
- `GET /auth/me` (authenticated)
- `GET /auth/users` (SUPER_ADMIN only)
- `PATCH /auth/users/{user_id}/role` (SUPER_ADMIN only)
- `DELETE /auth/users/{user_id}` (SUPER_ADMIN only)
- `POST /auth/logout` (authenticated session cleanup)
- `GET /dashboard/*` role-specific examples

## 4) Postman Samples

### Login

- Method: `POST`
- URL: `http://localhost:8000/auth/login`
- Body (JSON):

```json
{
  "email": "admin@gov.in",
  "password": "ChangeMe!12345"
}
```

Response contains `access_token`, role, and expiry.

### Create User (SUPER_ADMIN)

- Method: `POST`
- URL: `http://localhost:8000/auth/create-user`
- Header: `Authorization: Bearer <access_token>`
- Body (JSON):

```json
{
  "name": "Analyst User",
  "email": "analyst@gov.in",
  "password": "StrongPass!12345",
  "role": "SECURITY_ANALYST"
}
```

### Get Current User

- Method: `GET`
- URL: `http://localhost:8000/auth/me`
- Header: `Authorization: Bearer <access_token>`

### Admin User Listing

- Method: `GET`
- URL: `http://localhost:8000/auth/users`
- Header: `Authorization: Bearer <access_token>`

### Assign Role (SUPER_ADMIN)

- Method: `PATCH`
- URL: `http://localhost:8000/auth/users/<user_id>/role`
- Header: `Authorization: Bearer <access_token>`
- Body (JSON):

```json
{
  "role": "INCIDENT_RESPONDER"
}
```

### Delete User (SUPER_ADMIN)

- Method: `DELETE`
- URL: `http://localhost:8000/auth/users/<user_id>`
- Header: `Authorization: Bearer <access_token>`

## 5) Security Controls Implemented

- Bcrypt password hashing (`passlib` + `bcrypt`)
- JWT with expiration (`python-jose`)
- Gov-domain-only email enforcement
- Strict role guard dependency for route-level RBAC
- Login rate limiting (`5/minute`)
- Login and user-management security logs
- Input validation via Pydantic schemas
- HTTP-only auth cookie support + token fallback

## 6) Pipeline Integration Hook

Auth operations call `emit_auth_event(...)` in:

- `backend/app/services/security_event_service.py`

This is ready for Kafka producer integration for Spark pipeline consumption.
