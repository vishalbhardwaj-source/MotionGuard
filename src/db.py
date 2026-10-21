import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB_PATH = Path("outputs") / "motionguard.db"


def get_connection(db_path=None):
    """Get a thread-safe SQLite connection with WAL mode enabled."""
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def init_db(db_path=None):
    """Initialize SQLite database schema for incidents and dispatches."""
    conn = get_connection(db_path)
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                incident_id TEXT PRIMARY KEY,
                created_at_utc TEXT NOT NULL,
                scenario_id TEXT,
                timestamp_seconds REAL,
                threat_score INTEGER,
                threat_level TEXT,
                event_status TEXT,
                speed_kmh REAL,
                speed_limit_kmh REAL,
                overspeed_ratio REAL,
                reasons_json TEXT,
                factor_breakdown_json TEXT,
                event_source TEXT,
                track_id TEXT,
                vehicle_class TEXT,
                evidence_image TEXT,
                event_clip TEXT,
                delivery_status TEXT,
                review_status TEXT,
                review_history_json TEXT,
                notes TEXT
            );
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_incidents_review_status ON incidents(review_status);
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_incidents_threat_level ON incidents(threat_level);
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dispatches (
                dispatch_id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT,
                channel TEXT,
                status TEXT,
                recipient TEXT,
                carrier_network TEXT,
                dispatched_at TEXT,
                body TEXT,
                photo_attached INTEGER,
                created_at_utc TEXT
            );
        """)
    conn.close()


def save_incident_to_db(report, db_path=None):
    """Insert or replace an incident in the SQLite database."""
    init_db(db_path)
    conn = get_connection(db_path)
    with conn:
        conn.execute("""
            INSERT OR REPLACE INTO incidents (
                incident_id, created_at_utc, scenario_id, timestamp_seconds,
                threat_score, threat_level, event_status, speed_kmh,
                speed_limit_kmh, overspeed_ratio, reasons_json,
                factor_breakdown_json, event_source, track_id,
                vehicle_class, evidence_image, event_clip,
                delivery_status, review_status, review_history_json, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report.get("incident_id"),
            report.get("created_at_utc", datetime.now(timezone.utc).isoformat()),
            report.get("scenario_id"),
            report.get("timestamp_seconds"),
            report.get("threat_score"),
            report.get("threat_level"),
            report.get("event_status"),
            report.get("speed_kmh"),
            report.get("speed_limit_kmh"),
            report.get("overspeed_ratio"),
            json.dumps(report.get("reasons", [])),
            json.dumps(report.get("factor_breakdown", [])),
            report.get("event_source"),
            str(report.get("track_id")) if report.get("track_id") is not None else None,
            report.get("vehicle_class"),
            report.get("evidence_image"),
            report.get("event_clip"),
            report.get("delivery_status", "SIMULATED_ONLY"),
            report.get("review_status", "NEW"),
            json.dumps(report.get("review_history", [])),
            report.get("notes", ""),
        ))
    conn.close()
    return report


def update_incident_status_in_db(incident_id, new_status, notes=None, db_path=None):
    """Update review status and audit trail in SQLite."""
    init_db(db_path)
    conn = get_connection(db_path)
    now_utc = datetime.now(timezone.utc).isoformat()

    with conn:
        cursor = conn.execute(
            "SELECT review_status, review_history_json FROM incidents WHERE incident_id = ?",
            (incident_id,),
        )
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        current_history = json.loads(row["review_history_json"] or "[]")
        current_history.append({
            "previous_status": row["review_status"],
            "new_status": new_status,
            "changed_at_utc": now_utc,
            "notes": notes or "",
        })

        conn.execute("""
            UPDATE incidents
            SET review_status = ?, review_history_json = ?, notes = COALESCE(?, notes)
            WHERE incident_id = ?
        """, (new_status, json.dumps(current_history), notes, incident_id))

    conn.close()
    return True


def query_incidents_from_db(status=None, limit=100, db_path=None):
    """Query incidents from SQLite database with optional status filter."""
    init_db(db_path)
    conn = get_connection(db_path)
    query = "SELECT * FROM incidents"
    params = []

    if status:
        query += " WHERE review_status = ?"
        params.append(status)

    query += " ORDER BY created_at_utc DESC LIMIT ?"
    params.append(limit)

    cursor = conn.execute(query, params)
    rows = cursor.fetchall()
    results = []
    for r in rows:
        d = dict(r)
        d["reasons"] = json.loads(d["reasons_json"] or "[]")
        d["factor_breakdown"] = json.loads(d["factor_breakdown_json"] or "[]")
        d["review_history"] = json.loads(d["review_history_json"] or "[]")
        results.append(d)
    conn.close()
    return results


def save_dispatch_to_db(dispatch_res, db_path=None):
    """Save emergency dispatch record to SQLite database."""
    init_db(db_path)
    conn = get_connection(db_path)
    with conn:
        conn.execute("""
            INSERT INTO dispatches (
                message_id, channel, status, recipient,
                carrier_network, dispatched_at, body, photo_attached, created_at_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dispatch_res.get("message_id"),
            dispatch_res.get("channel"),
            dispatch_res.get("status"),
            dispatch_res.get("recipient"),
            dispatch_res.get("carrier_network"),
            dispatch_res.get("dispatched_at"),
            dispatch_res.get("body"),
            1 if dispatch_res.get("photo_attached") else 0,
            datetime.now(timezone.utc).isoformat(),
        ))
    conn.close()
