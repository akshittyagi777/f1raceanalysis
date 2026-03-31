"""
OpenF1 API client — pulls live lap, pit, position, and race control data.
No external dependencies (uses urllib from stdlib).
"""

import json
import time
import urllib.request
import urllib.parse
from functools import lru_cache

BASE_URL = "https://api.openf1.org/v1"

# Rate limit: 3 req/s free tier
_last_request_time = 0.0


def _fetch(endpoint: str, **params) -> list[dict]:
    """Fetch JSON from OpenF1 API with basic rate limiting."""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < 0.35:
        time.sleep(0.35 - elapsed)

    query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    url = f"{BASE_URL}/{endpoint}?{query}" if query else f"{BASE_URL}/{endpoint}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        _last_request_time = time.time()
        return json.loads(resp.read().decode())


@lru_cache(maxsize=32)
def get_session_key(year: int, country: str, session_type: str = "Race") -> int:
    """Look up a session key by year, country name, and session type.
    Prefers session_name='Race' over 'Sprint' when both have session_type='Race'."""
    data = _fetch("sessions", year=year, country_name=country, session_type=session_type)
    if not data:
        raise ValueError(f"No session found: {year} {country} {session_type}")
    # Prefer the main race over sprint (both have session_type="Race")
    for entry in data:
        if entry.get("session_name", "").lower() == "race":
            return entry["session_key"]
    return data[-1]["session_key"]


def get_laps(session_key: int, driver_number: int) -> dict[int, float]:
    """Return {lap_number: lap_duration} for a driver. Skips laps with no duration."""
    data = _fetch("laps", session_key=session_key, driver_number=driver_number)
    result = {}
    for row in data:
        lap = row.get("lap_number")
        dur = row.get("lap_duration")
        if lap is not None and dur is not None:
            result[int(lap)] = float(dur)
    return result


def get_sectors(session_key: int, driver_number: int) -> dict[int, tuple]:
    """Return {lap_number: (s1, s2, s3)} for a driver. Missing sectors stored as None."""
    data = _fetch("laps", session_key=session_key, driver_number=driver_number)
    result = {}
    for row in data:
        lap = row.get("lap_number")
        if lap is None:
            continue
        s1 = row.get("duration_sector_1")
        s2 = row.get("duration_sector_2")
        s3 = row.get("duration_sector_3")
        s1 = float(s1) if s1 is not None else None
        s2 = float(s2) if s2 is not None else None
        s3 = float(s3) if s3 is not None else None
        result[int(lap)] = (s1, s2, s3)
    return result


def get_pits(session_key: int) -> list[dict]:
    """Return list of pit stops: [{driver_number, lap_number, pit_duration}, ...]."""
    data = _fetch("pit", session_key=session_key)
    result = []
    for row in data:
        result.append({
            "driver_number": row.get("driver_number"),
            "lap_number": row.get("lap_number"),
            "pit_duration": row.get("pit_duration"),
        })
    return result


def get_driver_pits(session_key: int, driver_number: int) -> list[int]:
    """Return list of lap numbers where a driver pitted."""
    pits = get_pits(session_key)
    return sorted(p["lap_number"] for p in pits
                  if p["driver_number"] == driver_number and p["lap_number"] is not None)


def get_race_control(session_key: int) -> list[dict]:
    """Return race control messages: [{lap_number, category, message}, ...]."""
    data = _fetch("race_control", session_key=session_key)
    result = []
    for row in data:
        result.append({
            "lap_number": row.get("lap_number"),
            "category": row.get("category"),
            "message": row.get("message", ""),
        })
    return result


def get_safety_car_laps(session_key: int) -> list[tuple[int, int]]:
    """Return list of (sc_start_lap, sc_end_lap) for each safety car period."""
    msgs = get_race_control(session_key)
    periods = []
    sc_start = None
    for msg in msgs:
        text = msg["message"].upper()
        lap = msg["lap_number"]
        if lap is None:
            continue
        if "SAFETY CAR DEPLOYED" in text and "VIRTUAL" not in text:
            sc_start = lap
        elif sc_start is not None and ("SAFETY CAR IN THIS LAP" in text or "TRACK CLEAR" in text):
            periods.append((sc_start, lap))
            sc_start = None
    return periods


def get_restart_lap(session_key: int) -> int | None:
    """Return the lap number where racing resumed after the last SC period."""
    msgs = get_race_control(session_key)
    restart = None
    for msg in msgs:
        text = msg["message"].upper()
        if "SAFETY CAR IN THIS LAP" in text or "GREEN" in text:
            lap = msg["lap_number"]
            if lap is not None:
                restart = lap
    return restart


def get_total_laps(session_key: int) -> int:
    """Return the total number of laps in the race (from chequered flag message)."""
    msgs = get_race_control(session_key)
    for msg in msgs:
        if "CHEQUERED" in msg["message"].upper():
            return msg["lap_number"]
    # Fallback: find max lap from any driver
    return max(msg["lap_number"] for msg in msgs if msg["lap_number"] is not None)
