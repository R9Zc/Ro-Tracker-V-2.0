import requests
import json
import os
import time
from datetime import datetime, timedelta

# --- CONFIGURATION ---
USER_CONFIG = {
    "3263707365": "Saumya",
    "4491738101": "Saish",
    "1992158202": "Rushabh"  # Added Rushabh
}
USER_IDS = [3263707365, 4491738101, 1992158202]
STATUS_FILE = "status.json"
LOG_FILE = "logs.csv"

def get_ist_time():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

def run_tracker():
    # 1. Load Cache
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            try:
                history = json.load(f)
            except:
                history = {}
    else:
        history = {}

    # 2. Fetch Roblox Data
    url = "https://presence.roblox.com/v1/presence/users"
    try:
        response = requests.post(url, json={"userIds": USER_IDS})
        current_presences = response.json().get("userPresences", [])
    except Exception as e:
        print(f"Error fetching data: {e}")
        return history

    now_ist = get_ist_time()
    now_str = now_ist.strftime("%d-%m-%Y %I:%M %p")
    
    for user in current_presences:
        uid = str(user["userId"])
        # PresenceType 3 = In-Game
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
            
            # Write to CSV
            with open(LOG_FILE, "a") as f:
                f.write(f"{nickname},{game_played},{start_time_str},{now_str},{duration_str}\n")
            
            history[uid] = {"is_playing": False, "start_time": None, "game": None}
            print(f"Stopped: {nickname}")

    # 3. Save Cache
    with open(STATUS_FILE, "w") as f:
        json.dump(history, f)
    
    return history

if __name__ == "__main__":
    # The script stays alive for 20 minutes, checking every 60 seconds
    # This ensures 1-minute accuracy without hitting GitHub limits
    for i in range(20):
        print(f"Check {i+1} at {get_ist_time().strftime('%I:%M %p')}")
        run_tracker()
        time.sleep(60)
