# Brain 2.0 Orchestrator

Industrial, premium, ROI-focused AI CRM and automation platform architecture for the Indian SME market.

## One-Command Setup

```bash
docker-compose up --build
```

This project is Docker-first and does not require a local Python virtual environment.

## Environment Configuration

Create a `.env` file in the repository root with:

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `REVENUE_SECRET`

Backend runtime enforces `OAUTHLIB_INSECURE_TRANSPORT=1` for local containerized OAuth development.

## Port Mapping

| Service | Internal Port | Host Port |
| --- | --- | --- |
| Frontend (Vite/React) | 5173 | 5173 |
| Backend (Flask) | 8000 | 8000 |

Frontend API calls under `/api` are proxied to the backend service on the Docker bridge network.

## Deployment Guide (Hostinger / VPS)

1. Install Docker Engine and Docker Compose on your VPS.
2. Upload repository code to the server.
3. Create a production `.env` file with valid secrets.
4. Run:
   ```bash
   docker-compose up --build -d
   ```
5. Put Nginx/Caddy in front of ports `5173` and `8000` for domain + TLS termination.

## Multi-Tenant and Trial Guardrails

- All tenancy-sensitive flows must resolve data by dynamic `business_id` (never hardcoded IDs).
- New sign-ups must always start fresh provisioning logic (no demo fallback leakage).
- Trial urgency engine is based on `first_login_at + 72 hours`, with post-expiry lockout countdown handling.
