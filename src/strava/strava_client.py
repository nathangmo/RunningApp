import requests
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

class StravaClient:
    def __init__(self):
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.refresh_token = os.getenv("REFRESH_TOKEN")
        self.access_token = None

    def refresh_access_token(self):
        if not (self.client_id and self.client_secret and self.refresh_token):
            raise RuntimeError("Missing Strava credentials. Check your .env file.")

        response = requests.post(
            "https://www.strava.com/oauth/token",
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
            },
        )
        response.raise_for_status()
        data = response.json()
        self.access_token = data["access_token"]
        return self.access_token

    def get_activities(self, num_pages=3):
        if not self.access_token:
            raise RuntimeError("Access token missing. Call refresh_access_token() first.")

        activities = []
        for page in range(1, num_pages + 1):
            r = requests.get(
                "https://www.strava.com/api/v3/athlete/activities",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params={"per_page": 50, "page": page},
            )
            r.raise_for_status()
            page_acts = r.json()
            if not page_acts:
                break
            activities.extend(page_acts)
        return activities

    def activities_to_dataframe(self, activities):
        data = []
        for a in activities:
            if a["type"] != "Run":
                continue
            dist_km = a["distance"] / 1000
            pace = (a["moving_time"] / 60) / dist_km if dist_km > 0 else None
            data.append({
                "date": a["start_date_local"][:10],
                "name": a["name"],
                "distance_km": round(dist_km, 2),
                "pace_min_per_km": round(pace, 2) if pace else None,
                "time_min": round(a["moving_time"] / 60, 1),
            })

        return pd.DataFrame(data)

    def get_streams(self, activity_id):
        if not self.access_token:
            raise RuntimeError("Access token missing. Call refresh_access_token first.")

        url = f"https://www.strava.com/api/v3/activities/{activity_id}/streams"
        params = {
            "keys": "latlng,time,distance,altitude",
            "key_by_type": "true"
        }
        r = requests.get(url, headers={"Authorization": f"Bearer {self.access_token}"}, params=params)
        r.raise_for_status()
        return r.json()

