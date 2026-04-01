import requests
import json
import os
from datetime import datetime, timedelta

# --- CONFIGURATION ---
USER_CONFIG = {
    "3263707365": "Saumya",
    "4491738101": "Saish"
}
USER_IDS = [3263707365, 4491738101]
STATUS_FILE = "status.json"
LOG_FILE = "logs.csv"

def get_ist_time():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

def check_once():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            try:
                history = json.load(f)
            except:
                history = {}
    else:
        history = {}

    url = "https://presence.roblox.com/v1/presence/users"
    try:
        response = requests.post(url, json={"userIds": USER_IDS})
        current_presences = response.json().get("userPresences", [])
    except:
        return

    now_ist = get_ist_time()
    now_str = now_ist.strftime("%d-%m-%Y %I:%M %p")
    
    for user in current_presences:
        uid = str(user["userId"])
        # PresenceType 2 = Online (Website), 3 = In-Game
        is_playing = user.get("userPresenceType", 0) == 3 
        game_name = user.get("lastLocation", "Unknown Game")
        nickname = USER_CONFIG.get(uid, "Unknown")
        
        last_state = history.get(uid, {"is_playing": False, "start_time": None, "game": None})

        # Logic: Started Playing
        if is_playing and not last_state.get("is_playing"):
            history[uid] = {"is_playing": True, "start_time": now_str, "game": game_name}
            print(f"Started: {nickname} playing {game_name}")

        # Logic: Stopped Playing
        elif not is_playing and last_state.get("is_playing"):
            start_time_str = last_state["start_time"]
            start_dt = datetime.strptime(start_time_str, "%d-%m-%Y %I:%M %p")
            duration = now_ist - start_dt
            duration_str = str(duration).split(".")[0]
            
            game_played = last_state.get("game", "Unknown Game")
            
            # Fixed CSV line: No double commas
            with open(LOG_FILE, "a") as f:
                f.write(f"{nickname},{game_played},{start_time_str},{now_str},{duration_str}\n")
            
            history[uid] = {"is_playing": False, "start_time": None, "game": None}
            print(f"Stopped: {nickname}")

    with open(STATUS_FILE, "w") as f:
        json.dump(history, f)

if __name__ == "__main__":
    check_once()
