"""
Unit tests for timezone conversion and IST hour bucketing.
"""
from datetime import datetime, timezone, timedelta
from scoring import IST_ZONE, utc_to_ist

def test_utc_to_ist_conversion():
    # 00:30 UTC -> 06:00 IST (+5:30)
    utc_dt = datetime(2026, 10, 11, 0, 30, 0, tzinfo=timezone.utc)
    ist_dt = utc_to_ist(utc_dt)
    assert ist_dt.hour == 6
    assert ist_dt.minute == 0

def test_midnight_rollover():
    # 19:00 UTC -> next day 00:30 IST
    utc_dt = datetime(2026, 10, 11, 19, 0, 0, tzinfo=timezone.utc)
    ist_dt = utc_to_ist(utc_dt)
    assert ist_dt.day == 12
    assert ist_dt.hour == 0
    assert ist_dt.minute == 30
