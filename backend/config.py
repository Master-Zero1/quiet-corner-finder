"""
Configuration for Quiet Corner Finder
All numerical parameters are labeled as tunable defaults for testing.
"""
import os

BACKEND_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, '..'))
BASE_DIR = PROJECT_ROOT

def _resolve_db_path():
    """
    Returns path to SQLite database.
    Attempts local folder first; falls back to user app dir if Windows Controlled
    Folder Access blocks Python from writing inside Documents.
    """
    env_db = os.environ.get('QUIET_CORNER_DB')
    if env_db:
        return env_db
    local_db = os.path.join(PROJECT_ROOT, 'quiet_corners.db')
    try:
        # Test write permission in project directory
        test_file = os.path.join(PROJECT_ROOT, '.db_test_write')
        with open(test_file, 'w') as f:
            f.write('ok')
        os.remove(test_file)
        return local_db
    except (OSError, PermissionError):
        fallback_dir = os.path.join(os.path.expanduser('~'), '.quiet_place_finder')
        os.makedirs(fallback_dir, exist_ok=True)
        return os.path.join(fallback_dir, 'quiet_corners.db')

DATABASE = _resolve_db_path()

# Time-decay settings (defaults, tune during testing)
HALF_LIFE_MINUTES = 40.0         # Reports lose 50% weight every 40 minutes
MAX_REPORT_AGE_MINUTES = 180.0   # Only query reports from the last 3 hours

# Confidence tiers based on W = sum of weights (defaults, tune during testing)
CONFIDENCE_HIGH_THRESHOLD = 2.0    # W >= 2.0 -> High confidence ("Live — N reports")
CONFIDENCE_MEDIUM_THRESHOLD = 0.5  # 0.5 <= W < 2.0 -> Medium confidence ("Recent — limited")
                                   # W < 0.5 -> Baseline tier ("Usually [X] at this hour")

# Baseline minimum samples (defaults, tune during testing)
MIN_BASELINE_SAMPLES = 5           # Minimum reports in same hour-of-day bucket before using baseline average

# Anti-abuse rate limits (defaults, tune during testing)
RATE_LIMIT_MINUTES = 10            # 1 report per space per device per 10 minutes

# Timezone settings
CAMPUS_TIMEZONE = 'Asia/Kolkata'   # Indian Standard Time (UTC+5:30)

# Accuracy calculation window
ACCURACY_WINDOW_SIZE = 50          # Number of recent user-submitted reports to compute agreement score

# Demo mode flag
DEMO_MODE = True
