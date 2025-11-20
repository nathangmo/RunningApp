import pandas as pd
import altair as alt


def compute_weekly_volume(df: pd.DataFrame):
    df["date"] = pd.to_datetime(df["date"])
    df["week"] = df["date"].dt.isocalendar().week
    df["year"] = df["date"].dt.year

    weekly = (
        df.groupby(["year", "week"])
          .agg(
              distance_km=("distance_km", "sum"),
              avg_pace=("pace_min_per_km", "mean"),
              runs=("distance_km", "count")
          )
          .reset_index()
    )
    return weekly


def weekly_distance_chart(weekly_df):
    chart = alt.Chart(weekly_df).mark_bar().encode(
        x=alt.X("week:O", title="Week"),
        y=alt.Y("distance_km:Q", title="Weekly Distance (km)"),
        color="year:N",
        tooltip=["year", "week", "distance_km", "runs"]
    ).properties(
        width="container",
        height=300,
        title="Weekly Running Volume"
    )
    return chart


def pace_trend_chart(df):
    df["date"] = pd.to_datetime(df["date"])

    chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("pace_min_per_km:Q", title="Pace (min/km)"),
        tooltip=["date", "distance_km", "pace_min_per_km"]
    ).properties(
        width="container",
        height=300,
        title="Pace Trend Over Time"
    )
    return chart
