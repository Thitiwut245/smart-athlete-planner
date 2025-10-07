from datetime import date, timedelta
from typing import Dict, List

def generate_microcycles(start: date, weeks: int, availability: int, goal: str, level: str) -> List[Dict]:
    days: List[Dict] = []
    types_priority = {
        "fight_prep": ["technique","sparring","conditioning","recovery"],
        "general_skill": ["technique","conditioning","sparring","recovery"],
        "fat_loss": ["conditioning","technique","recovery","sparring"],
    }
    prio = types_priority.get(goal, types_priority["general_skill"])
    level_factor = {"beginner": 0.8, "intermediate": 1.0, "expert": 1.2}.get(level, 1.0)
    for w in range(weeks):
        used = 0
        for d in range(7):
            current = start + timedelta(days=w*7 + d)
            if used >= max(availability,1):
                days.append({"date": current, "type": "recovery", "minutes": int(30*level_factor), "rounds": 0, "rpe": 3})
                continue
            t = prio[used % len(prio)]
            base = {"technique": 8, "sparring": 6, "conditioning": 40, "recovery": 30}
            rounds = int(base[t]*level_factor) if t in ("technique","sparring") else 0
            minutes = rounds if t in ("technique","sparring") else int(base[t]*level_factor)
            rpe = {"technique": 6, "sparring": 8, "conditioning": 7, "recovery": 3}[t]
            days.append({"date": current, "type": t, "minutes": minutes, "rounds": rounds, "rpe": rpe})
            used += 1
    return days
