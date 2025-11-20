import json
from strava_client import StravaClient
import time
import os

os.makedirs("data/streams", exist_ok=True)

client = StravaClient()
client.refresh_access_token()

# Load activity list
acts = json.load(open("data/all_activities.json"))

for a in acts:
    act_id = a["id"]
    out_path = f"data/streams/{act_id}.json"

    if os.path.exists(out_path):
        continue

    streams = client.get_streams(act_id)
    json.dump(streams, open(out_path, "w"), indent=2)

    time.sleep(1)   # be polite to API
