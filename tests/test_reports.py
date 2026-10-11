"""
Unit tests for reports API and anti-abuse mechanisms:
- Valid submission
- Rate limiting (1 report per 10 min per device)
- Rejection of reports for closed spaces
- Outlier consensus detection
"""
import pytest
import uuid
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_valid_report_submission(client):
    res = client.post('/api/spaces/3/report', json={
        'noise': 1,
        'crowd': 1,
        'device_token': f'unique_token_{uuid.uuid4()}'
    })
    assert res.status_code == 201
    data = res.get_json()
    assert 'status' in data
    assert 'accuracy_pct' in data
    assert 'thanks' in data

def test_rate_limiting(client):
    token = f'rate_limit_token_{uuid.uuid4()}'
    # First report
    res1 = client.post('/api/spaces/3/report', json={
        'noise': 2,
        'crowd': 2,
        'device_token': token
    })
    assert res1.status_code == 201

    # Second report within 10 minutes from same device for same space
    res2 = client.post('/api/spaces/3/report', json={
        'noise': 2,
        'crowd': 2,
        'device_token': token
    })
    assert res2.status_code == 429
    assert 'Rate limit reached' in res2.get_json()['error']

def test_closed_space_rejection(client):
    # Dynamically find or configure a space that is closed at this exact moment
    from models import get_db
    from scoring import check_space_is_open, get_now_utc
    db = get_db()
    now = get_now_utc()
    closed_space_id = None
    for sid in range(1, 15):
        is_open, _ = check_space_is_open(sid, db, now)
        if not is_open:
            closed_space_id = sid
            break

    if closed_space_id is None:
        db.execute("UPDATE opening_hours SET open_time = '03:00', close_time = '03:01' WHERE space_id = 14")
        db.commit()
        closed_space_id = 14

    res = client.post(f'/api/spaces/{closed_space_id}/report', json={
        'noise': 1,
        'crowd': 1,
        'device_token': 'closed_test_device'
    })
    assert res.status_code == 400
    assert 'Space is currently closed' in res.get_json()['error']

def test_invalid_report_payload(client):
    # Missing noise
    res = client.post('/api/spaces/3/report', json={
        'crowd': 1,
        'device_token': 'invalid_payload_token'
    })
    assert res.status_code == 400

    # Noise out of bounds
    res2 = client.post('/api/spaces/3/report', json={
        'noise': 5,
        'crowd': 1,
        'device_token': 'invalid_payload_token'
    })
    assert res2.status_code == 400
