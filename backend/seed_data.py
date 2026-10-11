"""
Seed data generator for Quiet Corner Finder.
Creates 14 campus spaces with placeholder names, >=4 searchable attributes,
full opening hours, and realistic 48-hour report history for baseline and decay demonstration.
"""
import os
import sys
import random
import hashlib
from datetime import datetime, timezone, timedelta

# Ensure backend directory is in sys.path when executed directly
BACKEND_DIR = os.path.abspath(os.path.dirname(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import config
from models import init_db, get_db

IST_ZONE = timezone(timedelta(hours=5, minutes=30), name="IST")

SPACES_DATA = [
    {
        "name": "[SPACE_1] East Wing Reading Alcove",
        "building": "[BUILDING_A] Central Library",
        "lat": 12.9716, "lng": 77.5946,
        "description": "Quiet cushioned alcove with privacy partitions and natural daylight.",
        "attributes": {
            "seating": "Single armchairs with side tables, 14 seats",
            "typical_noise": "quiet",
            "indoor_outdoor": "indoor",
            "activities": "deep reading, silent study, laptop focus"
        },
        "hours": [(0, 7, "08:00", "22:00")] # Open 8am - 10pm every day
    },
    {
        "name": "[SPACE_2] Garden Terrace Seating",
        "building": "[BUILDING_B] Academic Block",
        "lat": 12.9722, "lng": 77.5952,
        "description": "Covered outdoor patio overlooking the botanical quad.",
        "attributes": {
            "seating": "Wooden park benches and stone tables, 20 seats",
            "typical_noise": "moderate",
            "indoor_outdoor": "outdoor",
            "activities": "light reading, relaxation, quiet conversations"
        },
        "hours": [(0, 7, "07:00", "19:00")]
    },
    {
        "name": "[SPACE_3] Ground Floor Study Pods",
        "building": "[BUILDING_A] Central Library",
        "lat": 12.9718, "lng": 77.5944,
        "description": "Semi-enclosed acoustic pods with charging outlets and reading lamps.",
        "attributes": {
            "seating": "Individual acoustic pods, 8 seats",
            "typical_noise": "quiet",
            "indoor_outdoor": "indoor",
            "activities": "individual exam prep, coding, audio lectures with headphones"
        },
        "hours": [(0, 7, "00:00", "23:59")] # 24/7 access
    },
    {
        "name": "[SPACE_4] 2nd Floor Mezzanine Corner",
        "building": "[BUILDING_C] Science Wing",
        "lat": 12.9729, "lng": 77.5938,
        "description": "Tucked away corner by the periodicals with wide garden view.",
        "attributes": {
            "seating": "Shared high tables with swivel stools, 12 seats",
            "typical_noise": "quiet",
            "indoor_outdoor": "indoor",
            "activities": "sketching, laptop work, problem sets"
        },
        "hours": [(0, 5, "08:30", "18:00")] # Weekdays only
    },
    {
        "name": "[SPACE_5] Quad Benches Under Banyan",
        "building": "[CAMPUS_QUAD_D] Central Grounds",
        "lat": 12.9712, "lng": 77.5960,
        "description": "Shaded circle of benches with natural breeze and birdsong.",
        "attributes": {
            "seating": "Ring benches, 25 seats",
            "typical_noise": "moderate",
            "indoor_outdoor": "outdoor",
            "activities": "resting between classes, contemplation, audiobooks"
        },
        "hours": [(0, 7, "06:00", "21:00")]
    },
    {
        "name": "[SPACE_6] Top Floor Silent Atrium",
        "building": "[BUILDING_E] Research Tower",
        "lat": 12.9735, "lng": 77.5950,
        "description": "Strict silence policy with vaulted glass skylights and panoramic view.",
        "attributes": {
            "seating": "Ergonomic mesh chairs and wide desks, 30 seats",
            "typical_noise": "quiet",
            "indoor_outdoor": "indoor",
            "activities": "silent revision, paper writing, deep research"
        },
        "hours": [(0, 7, "08:00", "20:00")]
    },
    {
        "name": "[SPACE_7] North Balcony Lounge",
        "building": "[BUILDING_F] Arts Pavilion",
        "lat": 12.9705, "lng": 77.5935,
        "description": "Open-air balcony with gentle shade awnings and soft seating.",
        "attributes": {
            "seating": "Bean bags and low lounge chairs, 10 seats",
            "typical_noise": "moderate",
            "indoor_outdoor": "outdoor",
            "activities": "creative breaks, mindfulness, notebook journaling"
        },
        "hours": [(0, 7, "09:00", "18:30")]
    },
    {
        "name": "[SPACE_8] Media Lab Annex Corner",
        "building": "[BUILDING_C] Science Wing",
        "lat": 12.9727, "lng": 77.5935,
        "description": "Dimly-lit peaceful corner behind the microfilms archive.",
        "attributes": {
            "seating": "Carrels with privacy felt boards, 10 seats",
            "typical_noise": "quiet",
            "indoor_outdoor": "indoor",
            "activities": "coding, quiet reading, laptop review"
        },
        "hours": [(0, 5, "09:00", "17:30")]
    },
    {
        "name": "[SPACE_9] Shaded Amphitheater Steps",
        "building": "[CAMPUS_QUAD_D] Central Grounds",
        "lat": 12.9709, "lng": 77.5965,
        "description": "Stepped stone seating shaded by tree canopy; peaceful off-peak.",
        "attributes": {
            "seating": "Tiered stone steps, 40 seats",
            "typical_noise": "moderate",
            "indoor_outdoor": "outdoor",
            "activities": "informal breaks, stretching, eating quiet snack"
        },
        "hours": [(0, 7, "06:00", "22:00")]
    },
    {
        "name": "[SPACE_10] Old Archway Rest Nook",
        "building": "[BUILDING_G] Heritage Hall",
        "lat": 12.9740, "lng": 77.5942,
        "description": "Historical stone archway corridor with cool ambient temperature.",
        "attributes": {
            "seating": "Built-in sandstone ledges with cushions, 8 seats",
            "typical_noise": "quiet",
            "indoor_outdoor": "indoor",
            "activities": "calm decompression, reading physical books"
        },
        "hours": [(0, 7, "08:00", "19:00")]
    },
    {
        "name": "[SPACE_11] Innovation Center Quiet Bay",
        "building": "[BUILDING_H] Tech Complex",
        "lat": 12.9720, "lng": 77.5925,
        "description": "Modern sound-dampened room dedicated to single-person work.",
        "attributes": {
            "seating": "Standing desks and ergonomic barstools, 12 seats",
            "typical_noise": "quiet",
            "indoor_outdoor": "indoor",
            "activities": "focused sprints, fast laptop revision"
        },
        "hours": [(0, 7, "08:00", "21:00")]
    },
    {
        "name": "[SPACE_12] Basement Micro-Hub",
        "building": "[BUILDING_B] Academic Block",
        "lat": 12.9724, "lng": 77.5956,
        "description": "Cool, low-footfall room shielded from campus exterior noise.",
        "attributes": {
            "seating": "Square tables with task chairs, 16 seats",
            "typical_noise": "quiet",
            "indoor_outdoor": "indoor",
            "activities": "exam preparation, group silence study"
        },
        "hours": [(0, 7, "08:00", "20:00")]
    },
    {
        "name": "[SPACE_13] Terrace Sunroom",
        "building": "[BUILDING_E] Research Tower",
        "lat": 12.9738, "lng": 77.5953,
        "description": "Glass-enclosed rooftop sunroom with indoor plants and soft lighting.",
        "attributes": {
            "seating": "Rattan chairs with pillows, 12 seats",
            "typical_noise": "quiet",
            "indoor_outdoor": "indoor",
            "activities": "relaxing, reading, unwinding"
        },
        "hours": [(0, 7, "09:00", "18:00")]
    },
    {
        "name": "[SPACE_14] South Corridor Window Seats",
        "building": "[BUILDING_F] Arts Pavilion",
        "lat": 12.9702, "lng": 77.5939,
        "description": "Long row of deep recessed bay windows facing the reflection pond.",
        "attributes": {
            "seating": "Padded window benches, 14 seats",
            "typical_noise": "moderate",
            "indoor_outdoor": "indoor",
            "activities": "reading, contemplation, listening to audio"
        },
        "hours": [(0, 7, "08:00", "19:00")]
    }
]

def hash_token(token):
    return hashlib.sha256(token.encode('utf-8')).hexdigest()

def seed_database(db_path=None):
    """Populates database with spaces, attributes, hours, and demo report history."""
    init_db(db_path)
    db = get_db(db_path)
    cursor = db.cursor()

    # Clear existing demo data
    cursor.execute("DELETE FROM reports")
    cursor.execute("DELETE FROM opening_hours")
    cursor.execute("DELETE FROM space_attributes")
    cursor.execute("DELETE FROM spaces")

    now_utc = datetime.now(timezone.utc)
    demo_devices = [hash_token(f"demo_device_{i}") for i in range(1, 20)]

    for space_item in SPACES_DATA:
        cursor.execute("""
            INSERT INTO spaces (name, building, lat, lng, description)
            VALUES (?, ?, ?, ?, ?)
        """, (
            space_item["name"],
            space_item["building"],
            space_item["lat"],
            space_item["lng"],
            space_item["description"]
        ))
        space_id = cursor.lastrowid

        # Insert >=4 attributes (Constraint 1 + EAV store)
        for key, val in space_item["attributes"].items():
            cursor.execute("""
                INSERT INTO space_attributes (space_id, key, value)
                VALUES (?, ?, ?)
            """, (space_id, key, val))

        # Insert opening hours
        for start_day, end_day, open_time, close_time in space_item["hours"]:
            for day in range(start_day, end_day):
                cursor.execute("""
                    INSERT INTO opening_hours (space_id, weekday, open_time, close_time)
                    VALUES (?, ?, ?, ?)
                """, (space_id, day, open_time, close_time))

        # Generate realistic report history over last 48 hours to establish hour baselines
        # Typical pattern: Morning (8-11: quiet=1), Lunch (12-14: moderate=2 or loud=3), Evening (quiet=1)
        reports_to_insert = []
        for hours_ago in range(3, 48, 2):
            report_time = now_utc - timedelta(hours=hours_ago, minutes=random.randint(0, 50))
            report_ist = report_time.astimezone(IST_ZONE)
            hour = report_ist.hour

            # Realistic noise distribution according to hour of day
            if 8 <= hour <= 11:
                noise = 1 if random.random() < 0.85 else 2
                crowd = 1 if random.random() < 0.70 else 2
            elif 12 <= hour <= 14:
                noise = 2 if random.random() < 0.60 else 3
                crowd = 2 if random.random() < 0.50 else 3
            elif 15 <= hour <= 18:
                noise = 1 if random.random() < 0.65 else 2
                crowd = 2 if random.random() < 0.70 else 1
            else:
                noise = 1
                crowd = 1

            device = random.choice(demo_devices)
            # Simulated history has NULL predicted_noise (seed data)
            reports_to_insert.append((
                space_id,
                noise,
                crowd,
                report_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                device,
                None,
                0
            ))

        cursor.executemany("""
            INSERT INTO reports (space_id, noise, crowd, created_at, device_hash, predicted_noise, is_outlier)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, reports_to_insert)

    # NOW SEED CONTROLLED RECENT REPORTS (<180 min) FOR IMMEDIATE DEMONSTRATION:
    # 1. Space 1: Multiple very fresh reports -> HIGH CONFIDENCE (Live — 3 reports)
    space1_reports = [
        (1, 1, 1, (now_utc - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ"), demo_devices[0], 1, 0),
        (1, 1, 1, (now_utc - timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:%SZ"), demo_devices[1], 1, 0),
        (1, 2, 2, (now_utc - timedelta(minutes=28)).strftime("%Y-%m-%dT%H:%M:%SZ"), demo_devices[2], 1, 0),
    ]
    cursor.executemany("""
        INSERT INTO reports (space_id, noise, crowd, created_at, device_hash, predicted_noise, is_outlier)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, space1_reports)

    # 2. Space 2: One moderate report 40 min ago -> MEDIUM CONFIDENCE (Recent — based on limited reports)
    space2_reports = [
        (2, 2, 2, (now_utc - timedelta(minutes=45)).strftime("%Y-%m-%dT%H:%M:%SZ"), demo_devices[3], 2, 0),
    ]
    cursor.executemany("""
        INSERT INTO reports (space_id, noise, crowd, created_at, device_hash, predicted_noise, is_outlier)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, space2_reports)

    # 3. Add a batch of reports with predicted_noise to demonstrate Accuracy Counter (Target ~82%)
    recent_accuracy_samples = []
    for i in range(30):
        t = now_utc - timedelta(minutes=10 + i * 5)
        # 80% agreement (within +-1)
        pred = random.choice([1, 2])
        if random.random() < 0.83:
            actual = pred # Exact or +-1
        else:
            actual = 3 if pred == 1 else 1 # Divergent
        recent_accuracy_samples.append((
            random.randint(3, 10),
            actual,
            pred,
            t.strftime("%Y-%m-%dT%H:%M:%SZ"),
            demo_devices[i % len(demo_devices)],
            pred,
            0
        ))
    cursor.executemany("""
        INSERT INTO reports (space_id, noise, crowd, created_at, device_hash, predicted_noise, is_outlier)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, recent_accuracy_samples)

    db.commit()
    db.close()
    print("Database successfully seeded with 14 campus spaces and realistic demo history.")

if __name__ == "__main__":
    seed_database()
