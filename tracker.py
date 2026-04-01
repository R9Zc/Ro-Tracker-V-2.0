import requests
import json
import os
from datetime import datetime, timedelta, timezone

USER_CONFIG = {"3263707365": "Saumya", "4491738101": "Saish", "1992158202": "Rushabh"}
USER_IDS = [3263707365, 4491738101, 1992158202]
STATUS_FILE = "status.json"
LOG_FILE = "logs.csv"

def get_ist_time():
    return datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)

def check_once():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            try: history = json.load(f)
            except: history = {}
    else: history = {}

    url = "https://presence.roblox.com/v1/presence/users"
    try:
        response = requests.post(url, json={"userIds": USER_IDS})
        data = response.json().get("userPresences", [])
    except: return

    now_ist = get_ist_time()
    now_str = now_ist.strftime("%d-%m-%Y %I:%M %p")
    
    for user in data:
        uid = str(user["userId"])
        is_playing = user.get("userPresenceType", 0) == 3 
        game_name = user.get("lastLocation", "Unknown Game")
        nickname = USER_CONFIG.get(uid, "Unknown")
        last = history.get(uid, {"is_playing": False, "start_time": None, "game": None})

        if is_playing and not last.get("is_playing"):
            history[uid] = {"is_playing": True, "start_time": now_str, "game": game_name}
        elif not is_playing and last.get("is_playing"):
            start_dt = datetime.strptime(last["start_time"], "%d-%m-%Y %I:%M %p")
            duration = now_ist.replace(tzinfo=None) - start_dt
            with open(LOG_FILE, "a") as f:
                f.write(f"{nickname},{last['game']},{last['start_time']},{now_str},{str(duration).split('.')[0]}\n")
            history[uid] = {"is_playing": False, "start_time": None, "game": None}

    with open(STATUS_FILE, "w") as f:
        json.dump(history, f)

if __name__ == "__main__":
    check_once()
