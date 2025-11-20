import streamlit as st
from strava_client import StravaClient
import pandas as pd

client = StravaClient()
client.refresh_access_token()

st.title("My Running Data")

# Load activities
acts = client.get_activities()
df = client.activities_to_dataframe(acts)

st.dataframe(df)

# Select an activity
activity_names = df["name"].tolist()
selected = st.selectbox("Select a run to see GPS data", activity_names)

if selected:
    # Find the activity ID
    match = next(a for a in acts if a["name"] == selected)
    act_id = match["id"]

    streams = client.get_streams(act_id)

    if "latlng" in streams:
        gps = streams["latlng"]["data"]

        # Create DataFrame with correct column names
        gps_df = pd.DataFrame(gps, columns=["lat", "lon"])

        st.subheader("Route Map")
        st.map(gps_df)

    else:
        st.write("No GPS data available for this run")

import plots

st.subheader("Weekly Training Volume")
weekly = plots.compute_weekly_volume(df)
st.altair_chart(plots.weekly_distance_chart(weekly), use_container_width=True)

st.subheader("Pace Trend")
st.altair_chart(plots.pace_trend_chart(df), use_container_width=True)
