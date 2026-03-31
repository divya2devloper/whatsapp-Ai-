# Gym-Brain

Gym-Brain is a 100% containerized, multi-tenant AI Orchestrator designed exclusively for Gym owners and Fitness Studios in the Indian market.

The only AI tool built to scale Indian Gyms.

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

- Supabase entities are `GymOwner (id, gmail, gym_name, plan_type, first_login_at)` and `GymBranch (id, owner_id, upi_id, branch_location, whatsapp_phone_id)`.
- New Gym login always provisions a fresh dashboard for tenant modules.
- No leakage is allowed into Hiring (Trainers) and WhatsApp (Member Chats) modules from any MASTER_DEMO data.
- Trial urgency engine is based on `first_login_at + 72 hours`, with post-expiry lockout countdown handling.
- Hinglish AI replies support member renewals, diet nudges, and personal training conversations.
- Google integration exposes Gmail readonly and Calendar events scopes for lead sync and free-trial booking workflows.
- Suggested RLS policy shape: `GymOwner.gmail == auth.jwt() ->> 'email'`.
