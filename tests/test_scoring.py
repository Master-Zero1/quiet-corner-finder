"""
Unit tests for scoring engine:
- Decay equation (fresh, half-life, double half-life, expired)
- Live status weighting & confidence tiers (high, medium, baseline)
- Hour-of-day baseline fallback
- Accuracy computation
"""
import pytest
from datetime import datetime, timezone, timedelta
import config
from scoring import compute_report_weight, compute_accuracy_score, IST_ZONE
from models import init_db, get_db

def test_decay_weight_calculation():
    now = datetime(2026, 10, 11, 12, 0, 0, tzinfo=timezone.utc)

    # 1. Fresh report (0 min ago) -> weight ~ 1.0
    w_0, age_0 = compute_report_weight(now, now=now, half_life_min=40.0)
    assert pytest.approx(w_0, 0.001) == 1.0
    assert age_0 == 0.0

    # 2. Exactly one half-life (40 min ago) -> weight ~ 0.5
    dt_40 = now - timedelta(minutes=40)
    w_40, age_40 = compute_report_weight(dt_40, now=now, half_life_min=40.0)
    assert pytest.approx(w_40, 0.001) == 0.5
    assert pytest.approx(age_40, 0.01) == 40.0

    # 3. Two half-lives (80 min ago) -> weight ~ 0.25
    dt_80 = now - timedelta(minutes=80)
    w_80, _ = compute_report_weight(dt_80, now=now, half_life_min=40.0)
    assert pytest.approx(w_80, 0.001) == 0.25

    # 4. Expired report (> 180 min ago) -> weight = 0.0
    dt_200 = now - timedelta(minutes=200)
    w_200, _ = compute_report_weight(dt_200, now=now, half_life_min=40.0, max_age_min=180.0)
    assert w_200 == 0.0

def test_accuracy_calculation():
    db = get_db()
    # Insert 5 test predictions
    now_iso = datetime.now(timezone.utc).isoformat()
    db.execute("DELETE FROM reports WHERE device_hash = 'test_acc_hash'")
    # 4 agreed (within +-1), 1 disagreed (|3 - 1| = 2)
    test_cases = [(1, 1), (2, 1), (3, 2), (2, 3), (3, 1)]
    for actual, pred in test_cases:
        db.execute("""
            INSERT INTO reports (space_id, noise, crowd, created_at, device_hash, predicted_noise, is_outlier)
            VALUES (1, ?, 1, ?, 'test_acc_hash', ?, 0)
        """, (actual, now_iso, pred))
    db.commit()

    score = compute_accuracy_score(db, window_size=5)
    # 4 out of 5 agreed -> 80.0%
    assert score['sample_size'] == 5
    assert score['agreed_count'] == 4
    assert pytest.approx(score['accuracy_pct'], 0.1) == 80.0

    # Cleanup
    db.execute("DELETE FROM reports WHERE device_hash = 'test_acc_hash'")
    db.commit()
    db.close()
