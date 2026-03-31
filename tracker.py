import requests
import json
import os
import time
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
    # Adds 5:30 to UTC for Indian Standard Time
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

def check_once():
    # Load Cache (Memory)
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            try:
                history = json.load(f)
            except:
                history = {}
    else:
        history = {}

    # Fetch Roblox Presence
    url = "https://presence.roblox.com/v1/presence/users"
    try:
        response = requests.post(url, json={"userIds": USER_IDS})
        current_presences = response.json().get("userPresences", [])
    except Exception as e:
        print(f"API Error: {e}")
        return

    now_ist = get_ist_time()
    now_str = now_ist.strftime("%d-%m-%Y %I:%M %p")
    
    for user in current_presences:
        uid = str(user["userId"])
        # PresenceType 2 = In Game, 3 = Studio
        is_playing = user["userPresenceType"] >= 2 
        game_name = user.get("lastLocation", "Unknown Game")
        nickname = USER_CONFIG.get(uid, "Unknown")
        
        last_state = history.get(uid, {"is_playing": False, "start_time": None, "game": None})

        # 1. STARTED PLAYING
        if is_playing and not last_state["is_playing"]:
            history[uid] = {
                "is_playing": True, 
                "start_time": now_str, 
                "game": game_name
            }
            print(f"{nickname} started playing {game_name}")

        # 2. STOPPED PLAYING
        elif not is_playing and last_state["is_playing"]:
            # Calculate Duration
            start_dt = datetime.strptime(last_state["start_time"], "%d-%m-%Y %I:%M %p")
            # Convert 'now' back to a comparable format for math
            duration = now_ist - (start_dt - timedelta(hours=0)) # Logic simplified for logging
            duration_str = str(duration).split(".")[0]
            
            # Write to CSV
            with open(LOG_FILE, "a") as f:
                f.write(f"{nickname},{last_state['game']},{last_state['start_time']},{now_str},{duration_str}\n")
            
            # Reset cache for user
            history[uid] = {"is_playing": False, "start_time": None, "game": None}
            print(f"{nickname} stopped playing.")

    # Save Cache back to file
    with open(STATUS_FILE, "w") as f:
        json.dump(history, f)

# --- 5 MINUTE INTERNAL LOOP ---
# GitHub runs this every 5 mins; this loop checks every 60s inside that window
for i in range(5):
    check_once()
    if i < 4: 
        time.sleep(60)
