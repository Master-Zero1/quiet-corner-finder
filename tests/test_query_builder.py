"""
Unit tests for generic query builder:
- Text search
- Attribute filtering
- Open now
- Injection protection
"""
from query_builder import build_spaces_query

def test_empty_query():
    sql, params = build_spaces_query({})
    assert "SELECT DISTINCT s.* FROM spaces s" in sql
    assert len(params) == 0

def test_text_search():
    sql, params = build_spaces_query({'q': 'Library'})
    assert "LIKE ?" in sql
    assert len(params) == 3
    assert params[0] == '%Library%'

def test_attribute_filter():
    sql, params = build_spaces_query({'activity': 'study', 'indoor_outdoor': 'indoor'})
    assert "space_attributes" in sql
    assert 'activities' in params
    assert '%study%' in params
    assert 'indoor_outdoor' in params
    assert '%indoor%' in params

def test_sql_injection_safety():
    malicious = "'; DROP TABLE spaces; --"
    sql, params = build_spaces_query({'q': malicious})
    # Must use parameterized placeholders
    assert "DROP TABLE" not in sql
    assert malicious in params[0]
