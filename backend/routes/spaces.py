"""
Spaces API endpoints for Quiet Corner Finder.
- GET /api/spaces: Filterable list with dynamic attributes, live/baseline status, and meta stats
- GET /api/spaces/<id>: Space details, 24-hr hourly pattern, and recent reports with decay weights
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from models import get_db, NOISE_LEVELS, CROWD_LEVELS
from query_builder import build_spaces_query
from scoring import resolve_space_status, compute_accuracy_score, compute_coverage_score, get_now_utc, compute_report_weight, utc_to_ist, parse_iso_datetime
import config

spaces_bp = Blueprint('spaces', __name__, url_prefix='/api')

@spaces_bp.route('/spaces', methods=['GET'])
def get_spaces():
    db = get_db()
    params = request.args.to_dict()

    sql, query_params = build_spaces_query(params)
    rows = db.execute(sql, query_params).fetchall()

    now_utc = get_now_utc()
    max_noise_filter = params.get('max_noise')
    if max_noise_filter:
        try:
            max_noise_filter = int(max_noise_filter)
        except ValueError:
            max_noise_filter = None

    spaces_list = []

    for r in rows:
        space_id = r['id']

        # Fetch all attributes (EAV store)
        attr_rows = db.execute("""
            SELECT key, value FROM space_attributes WHERE space_id = ?
        """, (space_id,)).fetchall()
        attributes = {a['key']: a['value'] for a in attr_rows}

        # Resolve status (live or hour baseline fallback)
        status_info = resolve_space_status(space_id, db, now=now_utc)

        # Apply max_noise filter if requested (Assumption A10)
        if max_noise_filter and status_info['status']['noise'] > max_noise_filter:
            continue

        space_obj = {
            "id": r['id'],
            "name": r['name'],
            "building": r['building'],
            "lat": r['lat'],
            "lng": r['lng'],
            "description": r['description'],
            "attributes": attributes,
            "status": status_info['status'],
            "is_open": status_info['is_open'],
            "next_change": status_info['next_change']
        }
        spaces_list.append(space_obj)

    accuracy_data = compute_accuracy_score(db)
    coverage_pct = compute_coverage_score(db)

    db.close()

    return jsonify({
        "spaces": spaces_list,
        "meta": {
            "count": len(spaces_list),
            "accuracy_pct": accuracy_data["accuracy_pct"],
            "accuracy_sample_size": accuracy_data["sample_size"],
            "coverage_pct": coverage_pct,
            "demo_mode": config.DEMO_MODE
        }
    })

@spaces_bp.route('/spaces/<int:space_id>', methods=['GET'])
def get_space_detail(space_id):
    db = get_db()
    space_row = db.execute("SELECT * FROM spaces WHERE id = ?", (space_id,)).fetchone()
    if not space_row:
        db.close()
        return jsonify({"error": "Space not found"}), 404

    now_utc = get_now_utc()

    # Attributes
    attr_rows = db.execute("SELECT key, value FROM space_attributes WHERE space_id = ?", (space_id,)).fetchall()
    attributes = {a['key']: a['value'] for a in attr_rows}

    # Resolved Status
    status_info = resolve_space_status(space_id, db, now=now_utc)

    # Opening hours
    hours_rows = db.execute("""
        SELECT weekday, open_time, close_time
        FROM opening_hours
        WHERE space_id = ?
        ORDER BY weekday, open_time
    """, (space_id,)).fetchall()
    hours_list = [{"weekday": h['weekday'], "open_time": h['open_time'], "close_time": h['close_time']} for h in hours_rows]

    # Hourly baseline distribution (0..23)
    all_reports = db.execute("""
        SELECT noise, crowd, created_at
        FROM reports
        WHERE space_id = ?
    """, (space_id,)).fetchall()

    hourly_buckets = {h: {"noise_sum": 0, "crowd_sum": 0, "count": 0} for h in range(24)}
    for rep in all_reports:
        dt_utc = parse_iso_datetime(rep['created_at'])
        dt_ist = utc_to_ist(dt_utc)
        h = dt_ist.hour
        hourly_buckets[h]["noise_sum"] += rep['noise']
        hourly_buckets[h]["crowd_sum"] += rep['crowd']
        hourly_buckets[h]["count"] += 1

    hourly_pattern = {}
    for h, data in hourly_buckets.items():
        if data["count"] > 0:
            hourly_pattern[str(h)] = {
                "avg_noise": round(data["noise_sum"] / data["count"], 1),
                "avg_crowd": round(data["crowd_sum"] / data["count"], 1),
                "sample_count": data["count"]
            }
        else:
            hourly_pattern[str(h)] = {
                "avg_noise": None,
                "avg_crowd": None,
                "sample_count": 0
            }

    # Recent 5 reports with decay weight
    recent_reports_raw = db.execute("""
        SELECT id, noise, crowd, created_at, is_outlier
        FROM reports
        WHERE space_id = ?
        ORDER BY created_at DESC
        LIMIT 5
    """, (space_id,)).fetchall()

    recent_reports = []
    for rep in recent_reports_raw:
        weight, age_min = compute_report_weight(rep['created_at'], now=now_utc)
        recent_reports.append({
            "noise": rep['noise'],
            "noise_label": NOISE_LEVELS.get(rep['noise'], "Quiet"),
            "crowd": rep['crowd'],
            "crowd_label": CROWD_LEVELS.get(rep['crowd'], "Empty"),
            "minutes_ago": round(age_min),
            "weight": round(weight, 3),
            "is_outlier": bool(rep['is_outlier'])
        })

    db.close()

    return jsonify({
        "space": {
            "id": space_row['id'],
            "name": space_row['name'],
            "building": space_row['building'],
            "lat": space_row['lat'],
            "lng": space_row['lng'],
            "description": space_row['description'],
            "attributes": attributes,
            "status": status_info['status'],
            "is_open": status_info['is_open'],
            "next_change": status_info['next_change'],
            "opening_hours": hours_list
        },
        "hourly_pattern": hourly_pattern,
        "recent_reports": recent_reports
    })
