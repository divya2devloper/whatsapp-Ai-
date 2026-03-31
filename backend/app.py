import os
from datetime import datetime, timedelta, timezone

from flask import Flask, jsonify, request
from flask_cors import CORS
from google_auth_oauthlib.flow import Flow
from supabase import create_client

os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

app = Flask(__name__)
CORS(app)

TRIAL_DURATION = timedelta(hours=72)
LOCKOUT_COUNTDOWN_MINUTES = 20
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# In-memory fallback to keep local development functional without Supabase credentials.
GYM_OWNERS = {}
GYM_BRANCHES = {}


@app.get("/health")
def health() -> tuple:
    return jsonify({"status": "ok", "service": "gym-brain-backend"}), 200


@app.get("/api/gym-owner/<owner_id>/trial-status")
def trial_status(owner_id: str) -> tuple:
    first_login_raw = request.args.get("first_login_at") or GYM_OWNERS.get(owner_id, {}).get("first_login_at")
    if not first_login_raw:
        return jsonify({"error": "first_login_at query param is required"}), 400

    try:
        first_login_at = datetime.fromisoformat(first_login_raw)
    except ValueError:
        return jsonify({"error": "first_login_at must be ISO-8601"}), 400
    if first_login_at.tzinfo is None:
        first_login_at = first_login_at.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    expires_at = first_login_at + TRIAL_DURATION
    expired = now >= expires_at

    remaining_minutes = max(0, int((expires_at - now).total_seconds() // 60))

    return (
        jsonify(
            {
                "owner_id": owner_id,
                "first_login_at": first_login_at.isoformat(),
                "expires_at": expires_at.isoformat(),
                "is_expired": expired,
                "remaining_minutes": remaining_minutes,
                "lockout_countdown_minutes": LOCKOUT_COUNTDOWN_MINUTES if expired else 0,
            }
        ),
        200,
    )


@app.post("/api/provision/business")
def provision_business() -> tuple:
    return provision_gym_owner()


@app.post("/api/provision/gym-owner")
def provision_gym_owner() -> tuple:
    payload = request.get_json(silent=True) or {}
    owner_id = payload.get("id")
    gmail = payload.get("gmail")
    if not owner_id or not gmail:
        return jsonify({"error": "id and gmail are required"}), 400

    owner_record = {
        "id": owner_id,
        "gmail": gmail,
        "gym_name": payload.get("gym_name", ""),
        "plan_type": payload.get("plan_type", "trial"),
        "first_login_at": payload.get("first_login_at") or datetime.now(timezone.utc).isoformat(),
    }
    branch_record = {
        "id": payload.get("branch_id", f"{owner_id}-primary"),
        "owner_id": owner_id,
        "upi_id": payload.get("upi_id", ""),
        "branch_location": payload.get("branch_location", ""),
        "whatsapp_phone_id": payload.get("whatsapp_phone_id", ""),
    }

    GYM_OWNERS[owner_id] = owner_record
    GYM_BRANCHES[branch_record["id"]] = branch_record

    if supabase:
        supabase.table("GymOwner").upsert(owner_record).execute()
        supabase.table("GymBranch").upsert(branch_record).execute()

    return (
        jsonify(
            {
                "message": "fresh gym owner provisioning initialized",
                "owner": owner_record,
                "branch": branch_record,
                "dashboard": {"hiring": [], "whatsapp": []},
            }
        ),
        201,
    )


@app.post("/api/ai/hinglish-reply")
def hinglish_reply() -> tuple:
    payload = request.get_json(silent=True) or {}
    member_name = payload.get("member_name", "Dost")
    topic = payload.get("topic", "membership")
    if topic == "renewal":
        message = (
            f"{member_name}, aapka membership renewal due hai. Aaj renew karoge to PT intro session free milega."
        )
    elif topic == "diet":
        message = f"{member_name}, aaj se protein-focused diet rakho aur paani 3 litre complete karo. Ho jayega!"
    else:
        message = f"{member_name}, free trial workout slot kal 7 baje available hai. Confirm kar doon?"
    return jsonify({"language": "hinglish", "message": message}), 200


@app.post("/api/whatsapp/route")
def whatsapp_route() -> tuple:
    payload = request.get_json(silent=True) or {}
    intent = payload.get("intent", "new_inquiry")
    route_map = {
        "new_inquiry": "sales_nurture",
        "renewal_reminder": "retention_followup",
        "trainer_escalation": "trainer_manager",
    }
    return jsonify({"intent": intent, "route": route_map.get(intent, "sales_nurture")}), 200


@app.get("/api/google/scopes")
def google_scopes() -> tuple:
    return jsonify({"scopes": GOOGLE_SCOPES}), 200


@app.post("/api/google/oauth/prepare")
def google_oauth_prepare() -> tuple:
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    if not client_id or not client_secret:
        return jsonify({"error": "google oauth client credentials are not configured"}), 400

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost:8000/oauth/callback"],
            }
        },
        scopes=GOOGLE_SCOPES,
    )
    authorization_url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true")
    return jsonify({"authorization_url": authorization_url, "state": state, "scopes": GOOGLE_SCOPES}), 200


@app.get("/api/security/rls")
def rls_policy() -> tuple:
    return (
        jsonify(
            {
                "policy_sql": (
                    "create policy gym_owner_access on GymOwner "
                    "for all using (gmail = auth.jwt() ->> 'email') "
                    "with check (gmail = auth.jwt() ->> 'email');"
                )
            }
        ),
        200,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
