import os
from datetime import datetime, timedelta, timezone

from flask import Flask, jsonify, request
from flask_cors import CORS

os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

app = Flask(__name__)
CORS(app)

TRIAL_DURATION = timedelta(hours=72)
LOCKOUT_COUNTDOWN_MINUTES = 20


@app.get("/health")
def health() -> tuple:
    return jsonify({"status": "ok", "service": "brain-2-backend"}), 200


@app.get("/api/business/<business_id>/trial-status")
def trial_status(business_id: str) -> tuple:
    first_login_raw = request.args.get("first_login_at")
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
                "business_id": business_id,
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
    payload = request.get_json(silent=True) or {}
    business_email = payload.get("gmail")
    if not business_email:
        return jsonify({"error": "gmail is required"}), 400

    # Fresh provisioning only; no demo fallback state is used.
    container_seed = {
        "business_id": payload.get("business_id"),
        "branch": payload.get("branch", "primary"),
        "upi": payload.get("upi"),
        "waba": payload.get("waba"),
    }

    return jsonify({"message": "fresh provisioning initialized", "container": container_seed}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
