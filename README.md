# Quiet Corner Finder

**Problem Statement 20** | Team 09 | Prithvi Chauhan

A web app that helps students find a quiet place on campus between classes. It lists campus spaces with seating, noise level, opening hours, and what each place suits, so you can filter by what you need and tap once to report how a place feels right now.

## Key features
- **One-tap anonymous reports.** No accounts, no sensors, no location tracking.
- **Old reports fade.** A report's weight halves every 40 minutes, so recent reports count more.
- **Confidence on every answer:** "Live", "Recent", or "Usually quiet at this hour" (an estimate from that hour's history when nobody has reported).
- **Self-measured accuracy.** Each new report is compared with what the app was showing just before it.
- **Abuse protection.** One report per space per 10 minutes per device, and closed spaces reject reports.

## Tech stack
Flask (Python), SQLite, HTML, CSS, JavaScript

## How to run
Requires Python 3.

```powershell
pip install -r requirements.txt
python run.py
```

Open **http://localhost:5000**. On Windows you can also double-click `run.bat`.

To open it on a phone, connect both devices to the same hotspot and visit `http://<your-laptop-ip>:5000`.
