"""
Stats API endpoint for Quiet Corner Finder.
- GET /api/stats: System-wide accuracy, coverage, and report counters
"""
from flask import Blueprint, jsonify
from datetime import datetime, timezone, timedelta
from models import get_db
from scoring import compute_accuracy_score, compute_coverage_score, get_now_utc
import config

stats_bp = Blueprint('stats', __name__, url_prefix='/api')

@stats_bp.route('/stats', methods=['GET'])
def get_stats():
    db = get_db()
    now_utc = get_now_utc()
    cutoff_24h = (now_utc - timedelta(hours=24)).isoformat()

    count_24h = db.execute("""
        SELECT COUNT(*) as c FROM reports WHERE created_at >= ?
    """, (cutoff_24h,)).fetchone()['c']

    total_spaces = db.execute("SELECT COUNT(*) as c FROM spaces").fetchone()['c']
    accuracy_data = compute_accuracy_score(db)
    coverage_pct = compute_coverage_score(db)

    db.close()

    return jsonify({
        "accuracy_pct": accuracy_data["accuracy_pct"],
        "accuracy_sample_size": accuracy_data["sample_size"],
        "agreed_count": accuracy_data["agreed_count"],
        "coverage_pct": coverage_pct,
        "total_spaces": total_spaces,
        "total_reports_24h": count_24h,
        "demo_mode": config.DEMO_MODE
    })
