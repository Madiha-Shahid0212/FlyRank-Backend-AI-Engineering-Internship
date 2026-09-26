# Auth API — Login & Protect (Supabase)

A secure FastAPI backend using Supabase Auth for user signup, login, logout, and protected routes secured with JWT bearer tokens. Public routes remain open; protected routes require a valid access token verified against Supabase on every request.

## What this project is

This API demonstrates a real authentication flow using Supabase as the Identity Provider (IdP):

1. A client signs up or logs in with an email and password.
2. Supabase validates the credentials and returns a JWT access token.
3. The client sends that token in the `Authorization: Bearer <token>` header on every request to a protected route.
4. The server verifies the token with Supabase before allowing access.

No passwords or cryptography are handled directly by this server — Supabase manages all of that securely.

## Setup

1. Clone the repository and navigate to this folder:
```
cd Week-04-Auth/auth-login-protect
```

2. Create a virtual environment and activate it:
```
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```
pip install fastapi uvicorn supabase python-dotenv
```

4. Copy `.env.example` to `.env` and fill in your own Supabase project URL and anon key (found in your Supabase Dashboard under Project Settings → API):
```
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_anon_key
PORT=8000
```

**Never commit your real `.env` file** — it is git-ignored, and only `.env.example` (with placeholder values) is committed.

## How to run

```
uvicorn main:app --reload --port 8000
```

The server will print `Server running and connected to Supabase` once it starts successfully. The API is available at `http://127.0.0.1:8000`.

## API Reference

| Method | Endpoint               | Auth Required | Description                              |
|--------|--------------------------|:--------------:|--------------------------------------------|
| GET    | `/`                      | No             | Root — confirms server is running          |
| POST   | `/auth/signup`           | No             | Create a new user account (Supabase)       |
| POST   | `/auth/login`            | No             | Log in and receive a JWT access token      |
| POST   | `/auth/logout`           | Yes            | Terminate the user session                 |
| GET    | `/public/info`           | No             | Public, unprotected data                   |
| GET    | `/protected/profile`     | Yes            | Read the authenticated user's profile      |
| GET    | `/protected/dashboard`   | Yes            | A second protected example route           |

### Status codes used

| Code | Meaning                                             |
|------|------------------------------------------------------|
| 200  | Successful login / read                              |
| 201  | Successful signup                                    |
| 204  | Successful logout (no content returned)              |
| 400  | Missing or invalid input (e.g. no email/password)    |
| 401  | Missing, invalid, expired, or tampered access token  |

## Example curl usage

**Sign up:**
```
curl -i -X POST http://127.0.0.1:8000/auth/signup -H "Content-Type: application/json" -d "{\"email\":\"you@example.com\", \"password\":\"yourpassword\"}"
```

**Log in:**
```
curl -i -X POST http://127.0.0.1:8000/auth/login -H "Content-Type: application/json" -d "{\"email\":\"you@example.com\", \"password\":\"yourpassword\"}"
```
This returns an `access_token` — copy it for the next requests.

**Access a protected route:**
```
curl -i http://127.0.0.1:8000/protected/profile -H "Authorization: Bearer <access_token>"
```

**Log out:**
```
curl -i -X POST http://127.0.0.1:8000/auth/logout -H "Authorization: Bearer <access_token>"
```

## Token verification

Protected routes use a shared `verify_token` dependency (FastAPI's `Depends`) instead of repeating auth-checking logic in every route. It:

- Extracts the bearer token from the `Authorization` header.
- Calls `supabase.auth.get_user(token)` to verify the token is valid and unexpired.
- Returns `401 Unauthorized` if the token is missing, malformed, tampered with, or expired.
- Returns the verified user object to the route if the token is valid.

This is wired into FastAPI's Swagger UI using the `HTTPBearer` security scheme, so protected routes show a lock icon and can be tested directly from the browser.

## Swagger UI

Visit `http://127.0.0.1:8000/docs`. Protected routes are marked with a lock icon. Click **Authorize**, paste your access token (without the `Bearer` prefix), and use **Try it out** to test protected endpoints directly from the browser.

![Swagger UI screenshot](swagger-screenshot.png)

## Security notes

- Real Supabase credentials live only in the local, git-ignored `.env` file.
- Only the Supabase **anon key** is used here (safe for client-side use); no service role key is exposed.
- Tokens are verified against Supabase on every protected request rather than trusted blindly — a tampered or expired token is always rejected.