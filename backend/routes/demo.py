"""
Demo simulation routes for Quiet Corner Finder.
Guarded by config.DEMO_MODE.
Allows the presenter to simulate live decay, submit reports at arbitrary past timestamps,
and 1-click reset the database during a live hackathon presentation.
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timezone, timedelta
import hashlib
from models import get_db
from scoring import resolve_space_status, compute_accuracy_score, get_now_utc
from seed_data import seed_database
import config

demo_bp = Blueprint('demo', __name__, url_prefix='/api/demo')

@demo_bp.route('/simulate', methods=['POST'])
def simulate_report():
    if not config.DEMO_MODE:
        return jsonify({"error": "Demo mode is disabled"}), 403

    data = request.get_json(silent=True) or {}
    space_id = data.get('space_id', 1)
    noise = int(data.get('noise', 2))
    crowd = int(data.get('crowd', 2))
    minutes_ago = float(data.get('minutes_ago', 0))

    if noise not in (1, 2, 3) or crowd not in (1, 2, 3):
        return jsonify({"error": "Invalid noise or crowd value"}), 400

    now_utc = get_now_utc()
    report_dt = now_utc - timedelta(minutes=minutes_ago)
    report_iso = report_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    db = get_db()
    # Capture current prediction
    status_before = resolve_space_status(space_id, db, now=now_utc)
    pred_noise = status_before['status']['noise']

    device_hash = hashlib.sha256(f"demo_sim_{now_utc.timestamp()}".encode('utf-8')).hexdigest()

    db.execute("""
        INSERT INTO reports (space_id, noise, crowd, created_at, device_hash, predicted_noise, is_outlier)
        VALUES (?, ?, ?, ?, ?, ?, 0)
    """, (space_id, noise, crowd, report_iso, device_hash, pred_noise))
    db.commit()

    updated_status = resolve_space_status(space_id, db, now=now_utc)
    accuracy_data = compute_accuracy_score(db)
    db.close()

    return jsonify({
        "simulated": True,
        "space_id": space_id,
        "minutes_ago": minutes_ago,
        "status": updated_status['status'],
        "accuracy_pct": accuracy_data["accuracy_pct"]
    })

@demo_bp.route('/reset', methods=['POST'])
def reset_demo_database():
    if not config.DEMO_MODE:
        return jsonify({"error": "Demo mode is disabled"}), 403

    seed_database()
    return jsonify({
        "status": "reset_complete",
        "message": "Database reset and re-seeded with pristine demo data."
    })
