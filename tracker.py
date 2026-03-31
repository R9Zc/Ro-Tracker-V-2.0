import requests
import json
import os
from datetime import datetime, timedelta

# --- CONFIGURATION ---
# Mapping IDs to names for easier tracking
USER_CONFIG = {
    "3263707365": "Saumya",
    "4491738101": "Saish"
}
USER_IDS = [3263707365, 4491738101]
STATUS_FILE = "status.json"
LOG_FILE = "logs.csv"

def get_ist_time():
    # GitHub uses UTC, so we add 5.5 hours for India Standard Time
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

def get_presence_data(ids):
    url = "https://presence.roblox.com/v1/presence/users"
    try:
        response = requests.post(url, json={"userIds": ids})
        return response.json().get("userPresences", [])
    except Exception as e:
        print(f"API Error: {e}")
        return []

def main():
    # Load previous status memory
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            history = json.load(f)
    else:
        history = {}

    current_presences = get_presence_data(USER_IDS)
    now_ist = get_ist_time()
    now_str = now_ist.strftime("%d-%m-%Y %I:%M %p") # DD-MM-YYYY HH:MM AM/PM
    
    for user in current_presences:
        uid = str(user["userId"])
        # PresenceType 2 = In Game, 3 = Studio
        is_playing = user["userPresenceType"] >= 2 
        game_name = user.get("lastLocation", "Unknown Game")
        nickname = USER_CONFIG.get(uid, "Unknown")
        
        # Get last state or set default
        last_state = history.get(uid, {"is_playing": False, "start_time": None, "game": None})

        # 1. STARTED PLAYING
        if is_playing and not last_state["is_playing"]:
            history[uid] = {
                "is_playing": True, 
                "start_time": now_str, 
                "game": game_name
            }

        # 2. STOPPED PLAYING
        elif not is_playing and last_state["is_playing"]:
            # Calculate duration
            start_dt = datetime.strptime(last_state["start_time"], "%d-%m-%Y %I:%M %p")
            duration = now_ist - (start_dt - timedelta(hours=5, minutes=30)) # Back-calc to UTC for math
            
            # Simple duration format (e.g. 1:20:00)
            duration_str = str(duration).split(".")[0]
            
            # Write to CSV: Name, Game, Start, End, Duration
            with open(LOG_FILE, "a") as f:
                f.write(f"{nickname},{last_state['game']},{last_state['start_time']},{now_str},{duration_str}\n")
            
            # Reset history for this user
            history[uid] = {"is_playing": False, "start_time": None, "game": None}

    # Save memory to status.json
    with open(STATUS_FILE, "w") as f:
        json.dump(history, f)

if __name__ == "__main__":
    main()
