import requests
import json
import os
import time
from datetime import datetime, timedelta

USER_CONFIG = {
    "3263707365": "Saumya",
    "4491738101": "Saish",
    "1992158202": "Rushabh"
}
USER_IDS = [3263707365, 4491738101, 1992158202]
STATUS_FILE = "status.json"
LOG_FILE = "logs.csv"

def get_ist_time():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

def check_once():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            try: history = json.load(f)
            except: history = {}
    else: history = {}

    url = "https://presence.roblox.com/v1/presence/users"
    try:
        response = requests.post(url, json={"userIds": USER_IDS})
        current_presences = response.json().get("userPresences", [])
    except: return history

    now_ist = get_ist_time()
    now_str = now_ist.strftime("%d-%m-%Y %I:%M %p")
    
    for user in current_presences:
        uid = str(user["userId"])
        is_playing = user.get("userPresenceType", 0) == 3 
        game_name = user.get("lastLocation", "Unknown Game")
        nickname = USER_CONFIG.get(uid, "Unknown")
        last_state = history.get(uid, {"is_playing": False, "start_time": None, "game": None})

        if is_playing and not last_state.get("is_playing"):
            history[uid] = {"is_playing": True, "start_time": now_str, "game": game_name}
        elif not is_playing and last_state.get("is_playing"):
            start_dt = datetime.strptime(last_state["start_time"], "%d-%m-%Y %I:%M %p")
            duration = now_ist - start_dt
            with open(LOG_FILE, "a") as f:
                f.write(f"{nickname},{last_state['game']},{last_state['start_time']},{now_str},{str(duration).split('.')[0]}\n")
            history[uid] = {"is_playing": False, "start_time": None, "game": None}

    with open(STATUS_FILE, "w") as f:
        json.dump(history, f)
    return history

if __name__ == "__main__":
    # Checks 5 times (once every 60 seconds)
    for i in range(5):
        check_once()
        if i < 4: # Don't sleep after the last check
            time.sleep(60)
