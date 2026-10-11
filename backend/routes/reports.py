"""
Reports API endpoint for Quiet Corner Finder.
- POST /api/spaces/<id>/report:
  - Validates noise (1..3) and crowd (1..3)
  - Hashes client-generated device_token with SHA-256 (no accounts)
  - Rate limits: 1 report per space per 10 minutes per device
  - Rejects reports for closed spaces
  - Performs outlier dampening if report clashes strongly with consensus
  - Captures predicted_noise snapshot for self-measured accuracy
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timezone, timedelta
import hashlib
from models import get_db, NOISE_LEVELS, CROWD_LEVELS
from scoring import resolve_space_status, compute_accuracy_score, get_now_utc, check_space_is_open
import config

reports_bp = Blueprint('reports', __name__, url_prefix='/api')

@reports_bp.route('/spaces/<int:space_id>/report', methods=['POST'])
def submit_report(space_id):
    data = request.get_json(silent=True) or {}

    noise = data.get('noise')
    crowd = data.get('crowd')
    device_token = str(data.get('device_token', '')).strip()

    # 1. Validation
    if noise not in (1, 2, 3):
        return jsonify({"error": "Noise level must be 1 (Quiet), 2 (Moderate), or 3 (Loud)"}), 400
    if crowd not in (1, 2, 3):
        return jsonify({"error": "Crowd level must be 1 (Empty), 2 (Some seats), or 3 (Crowded)"}), 400
    if not device_token:
        return jsonify({"error": "Missing device token"}), 400

    device_hash = hashlib.sha256(device_token.encode('utf-8')).hexdigest()
    now_utc = get_now_utc()
    db = get_db()

    # 2. Space Existence Check
    space_row = db.execute("SELECT id FROM spaces WHERE id = ?", (space_id,)).fetchone()
    if not space_row:
        db.close()
        return jsonify({"error": "Space not found"}), 404

    # 3. Closed Space Rejection Check (PRD FR12)
    is_open, open_info = check_space_is_open(space_id, db, check_dt=now_utc)
    if not is_open:
        db.close()
        return jsonify({"error": f"Space is currently closed ({open_info})"}), 400

    # 4. Rate Limiting Check (PRD FR11: 1 report per space per 10 min per device)
    rate_limit_cutoff = (now_utc - timedelta(minutes=config.RATE_LIMIT_MINUTES)).isoformat()
    recent_device_report = db.execute("""
        SELECT created_at FROM reports
        WHERE space_id = ? AND device_hash = ? AND created_at >= ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (space_id, device_hash, rate_limit_cutoff)).fetchone()

    if recent_device_report:
        db.close()
        return jsonify({
            "error": f"Rate limit reached. You can submit another report for this space in {config.RATE_LIMIT_MINUTES} minutes."
        }), 429

    # 5. Capture predicted_noise before inserting new report (PRD A7.6)
    current_status_info = resolve_space_status(space_id, db, now=now_utc)
    predicted_noise = current_status_info['status']['noise']

    # 6. Outlier consensus dampening (PRD FR13)
    is_outlier = 0
    weight_sum = current_status_info['status'].get('weight_sum', 0.0)
    if weight_sum >= config.CONFIDENCE_HIGH_THRESHOLD:
        if abs(noise - predicted_noise) >= 2:
            is_outlier = 1

    # 7. Insert new report
    created_at_iso = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    db.execute("""
        INSERT INTO reports (space_id, noise, crowd, created_at, device_hash, predicted_noise, is_outlier)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (space_id, noise, crowd, created_at_iso, device_hash, predicted_noise, is_outlier))
    db.commit()

    # 8. Re-evaluate updated status and accuracy
    updated_status_info = resolve_space_status(space_id, db, now=now_utc)
    accuracy_data = compute_accuracy_score(db)

    db.close()

    return jsonify({
        "status": updated_status_info['status'],
        "accuracy_pct": accuracy_data["accuracy_pct"],
        "is_outlier_flagged": bool(is_outlier),
        "thanks": f"Report received! Fades smoothly over ~{int(config.HALF_LIFE_MINUTES)} min."
    }), 201
