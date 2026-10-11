# 🤫 Quiet Corner Finder (PS20)

> **Final Round Hackathon Solution** — Real-Time Campus Quiet Space Discovery using time-decayed crowd reports, confidence tiers, hour-of-day baselines, and self-measured accuracy. Zero sensors, zero user accounts, zero continuous location tracking.

---

## 📁 Clean & Professional Architecture

The codebase is organized into modular frontend and backend packages:

```
quiet_place_finder/
│
├── backend/                  # Python Flask REST API & Business Logic
│   ├── routes/               # API Blueprints
│   │   ├── __init__.py       # Blueprint registry
│   │   ├── spaces.py         # Space queries, details & 24h patterns
│   │   ├── reports.py        # Anonymous reporting & anti-abuse checks
│   │   ├── stats.py          # Campus pulse & accuracy aggregation
│   │   └── demo.py           # Simulation & instant database reset
│   ├── app.py                # Flask application factory
│   ├── config.py             # Tunable time-decay constants & configs
│   ├── models.py             # SQLite schema & database connection helpers
│   ├── scoring.py            # Exponential decay math & confidence tiers
│   ├── query_builder.py      # Dynamic parameter-to-EAV query mapper
│   └── seed_data.py          # 14 campus spaces & 48h realistic history
│
├── frontend/                 # User Interface & Client Assets
│   ├── templates/
│   │   └── index.html        # Modern editorial campus acoustic map & minigame
│   └── static/
│       ├── css/
│       │   └── custom.css    # Supplemental utility styling
│       └── js/
│           └── main.js       # Client helper utilities
│
├── tests/                    # Automated Test Suite (Pytest)
│   ├── conftest.py           # Backend path auto-registration
│   ├── test_query_builder.py # Query builder & injection tests
│   ├── test_reports.py       # Submission, rate limits & closure checks
│   ├── test_scoring.py       # Exponential decay & confidence tests
│   └── test_timezone.py      # IST timezone conversions
│
├── run.py                    # Root entry point launcher
├── run.bat                   # 1-click Windows startup script
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## ⚡ Quick Start (One Command)

### On Windows
```powershell
python run.py
```
Or double-click `run.bat`.

The application will start on:
- **Laptop browser**: `http://localhost:5000`
- **Mobile phone on Hotspot**: `http://<YOUR_LAPTOP_IP>:5000` (Find IP via `ipconfig`)

---

## 🧪 Running Automated Tests

Run the full pytest suite (12 automated unit tests covering decay equations, confidence thresholds, rate limiting, and timezone handling):

```powershell
python -m pytest
```

---

## 🎯 5 Core Hackathon Differentiators

1. **Time-Decayed Consensus (Not just last report)**:
   - Each report's weight $W = 0.5^{(\text{age\_minutes} / 40)}$.
   - Stale reports fade smoothly over ~3 hours without abrupt cutoff.
2. **Confidence & Freshness Tiers**:
   - $W \ge 2.0$: **Live — N reports** (High confidence, emerald pill)
   - $0.5 \le W < 2.0$: **Recent — limited reports** (Medium confidence, amber pill)
   - $W < 0.5$: **Usually [X] at this hour** (Baseline fallback, indigo pill)
3. **Hour-of-Day Baseline Fallback**:
   - Never shows blank or stale data. When no recent reports exist, the system predicts noise based on past reports in the same Indian Standard Time (IST) hour-of-day bucket.
4. **Self-Measured Accuracy Counter**:
   - When each report is submitted, the system captures what the app was showing (`predicted_noise`) just before insertion.
   - Agreement ($|\text{reported} - \text{predicted}| \le 1$) is calculated and displayed live in the header.
5. **Completely Anonymous & Zero Tracking**:
   - Client-side UUID token stored in `localStorage`, SHA-256 hashed on the server.
   - Rate limit: 1 report per space per 10 minutes per device.
   - Reports for closed spaces are automatically rejected.

---

## 🎤 3-Minute Hackathon Demo Script

Follow this step-by-step walkthrough in front of the judges:

1. **The Core Experience (30s)**:
   - Open `http://localhost:5000` on mobile or desktop.
   - Show the cards: Explain the distinct **Status Pills** and **Confidence Tiers** (`Live`, `Recent`, `Usually quiet at this hour`).
   - Point out the **Accuracy Badge** in the header (`~94%` self-measured agreement).

2. **Search & Dynamic Filters (30s)**:
   - Tap **🟢 Open Now**: Shows only spaces open at current campus time.
   - Tap **🤫 Quiet Only**: Filters by current resolved live/baseline status.
   - Tap **📚 Silent Study** or **🏢 Indoor**: Demonstrates the EAV attribute filtering (Constraint 1).

3. **Space Details & 24-Hour Baseline (45s)**:
   - Tap any card to open the **Space Detail View**.
   - Show the **24-Hour Pattern Bar Chart**: Explain that when no students are reporting, the app automatically falls back to this hour's historical baseline.
   - Show the **Recent Reports (Decaying)** list with visible mathematical decay weights (e.g. weight $0.81$, $0.50$).

4. **1-Tap Anonymous Report & Anti-Abuse (45s)**:
   - Tap **Update ✍️** on an open space (e.g. Space 3).
   - Select **Moderate** + **Some Seats** and tap Submit.
   - Point out the instant update on the card and toast notification!
   - Immediately tap **Update ✍️** again: Point out the **Anti-Abuse Rate Limit** alert ("Rate limit reached. Please wait before submitting another report for this space").

5. **Demo Toolbar & Decay Simulation (30s)**:
   - Click **Demo Tools ⚙️** at the top right.
   - Pick a space and choose **Simulated Age: 40m ago (1 Half-life, weight = 0.5)** or **190m ago (Expired)**.
   - Click **⚡ Inject Report**: Show the judges how the score decays and confidence shifts automatically!
