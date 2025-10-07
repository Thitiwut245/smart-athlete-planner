# app/routers/exercise.py
from fastapi import APIRouter, Depends, HTTPException, Response
from ..deps import get_current_user
import os, requests, random, json, time
from pathlib import Path
from typing import Optional

router = APIRouter(
    prefix="/api/v1/exercise",
    tags=["exercise"],
    dependencies=[Depends(get_current_user)]
)

API_KEY: str = os.getenv("EXERCISE_API_KEY", "")
OFFLINE_ONLY: bool = os.getenv("EXERCISE_OFFLINE", "false").lower() in ("1", "true", "yes")
FALLBACK_PATH = Path(__file__).resolve().parents[1] / "data" / "exercises_fallback.json"

ALLOWED_MUSCLES = {
    "abdominals","abductors","adductors","biceps","calves","chest","forearms",
    "glutes","hamstrings","lats","lower_back","middle_back","neck",
    "quadriceps","traps","triceps","shoulders"
}

# ---- tiny in-memory cache (key -> (ts, data)) ----
_CACHE: dict[str, tuple[float, list]] = {}
CACHE_TTL = 60 * 10  # 10 minutes


def _cache_get(key: str) -> Optional[list]:
    now = time.time()
    entry = _CACHE.get(key)
    if not entry:
        return None
    ts, data = entry
    if now - ts > CACHE_TTL:
        _CACHE.pop(key, None)
        return None
    return data


def _cache_set(key: str, data: list) -> None:
    _CACHE[key] = (time.time(), data)


def _load_fallback() -> list:
    if not FALLBACK_PATH.exists():
        return []
    try:
        with open(FALLBACK_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _filter(items: list, muscle: Optional[str] = None, type: Optional[str] = None) -> list:
    def ok(item):
        if muscle and item.get("muscle") != muscle:
            return False
        if type and item.get("type") != type:
            return False
        return True
    return [x for x in items if ok(x)]


def _call_api(url: str) -> list:
    """Call remote API with small retry & timeout."""
    last_err = None
    for attempt in range(3):
        try:
            r = requests.get(url, headers={"X-Api-Key": API_KEY}, timeout=8)
            if r.status_code == 200:
                return r.json()
            last_err = HTTPException(r.status_code, r.text)
        except requests.RequestException as e:
            last_err = e
        time.sleep(0.6 * (attempt + 1))
    # If we reach here, all attempts failed
    if isinstance(last_err, HTTPException):
        raise last_err
    raise HTTPException(502, "Exercise API unreachable")


def _search_remote(muscle: Optional[str], difficulty: Optional[str], type: Optional[str] = None) -> list:
    qs = []
    if muscle:
        qs.append(f"muscle={muscle}")
    if difficulty:
        qs.append(f"difficulty={difficulty}")
    if type:
        qs.append(f"type={type}")
    url = "https://api.api-ninjas.com/v1/exercises" + ("?" + "&".join(qs) if qs else "")
    if not API_KEY:
        raise HTTPException(500, "Missing EXERCISE_API_KEY")
    return _call_api(url)


def _search(muscle: Optional[str], difficulty: Optional[str], type: Optional[str]) -> tuple[list, str]:
    key = f"{muscle or ''}|{difficulty or ''}|{type or ''}"
    cached = _cache_get(key)
    if cached is not None:
        return cached, "cache"

    if OFFLINE_ONLY:
        data = _filter(_load_fallback(), muscle, type)
        if difficulty:
            data = [d for d in data if d.get("difficulty") == difficulty]
        _cache_set(key, data)
        return data, "fallback"

    try:
        data = _search_remote(muscle, difficulty, type)
        _cache_set(key, data)
        return data, "remote"
    except HTTPException:
        data = _filter(_load_fallback(), muscle, type)
        if difficulty:
            data = [d for d in data if d.get("difficulty") == difficulty]
        _cache_set(key, data)
        return data, "fallback"



@router.get("")
def search(muscle: Optional[str] = None, difficulty: Optional[str] = None, type: Optional[str] = None, response: Response = None):
    if muscle and muscle not in ALLOWED_MUSCLES:
        raise HTTPException(400, f"Unsupported muscle '{muscle}'")
    data, source = _search(muscle, difficulty, type)
    if response is not None:
        response.headers["X-Exercise-Source"] = source
    return data


@router.get("/random")
def random_ex(muscle: Optional[str] = None, difficulty: Optional[str] = None, type: Optional[str] = None, response: Response = None):
    if muscle and muscle not in ALLOWED_MUSCLES:
        raise HTTPException(400, f"Unsupported muscle '{muscle}'")
    data, source = _search(muscle, difficulty, type)
    if not data:
        raise HTTPException(404, "No exercises available (API down and no local match).")
    if response is not None:
        response.headers["X-Exercise-Source"] = source
    return random.choice(data)
