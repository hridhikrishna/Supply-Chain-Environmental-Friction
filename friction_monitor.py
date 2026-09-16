from datetime import datetime
import pandas as pd
import requests

# 1. Define Key Logistics Checkpoints (e.g., Wayanad-to-Calicut Mountain Corridor)
# Format: {"name": "Checkpoint Name", "lat": latitude, "lon": longitude}
ROUTE_CHECKPOINTS = [
    {"name": "Thamarassery Churam (Hairpin 9)", "lat": 11.4885, "lon": 76.0822},
    {"name": "Vythiri Pass Summit", "lat": 11.5515, "lon": 76.0448},
    {"name": "Kalpetta Highway Junction", "lat": 11.6054, "lon": 76.0830},
    {"name": "Sulthan Bathery Foothills", "lat": 11.6667, "lon": 76.2667},
]

print("Evaluating environmental friction and hazard scores for transit route...")

checkpoint_reports = []


def calculate_friction_score(weather):
  """Calculates an environmental friction score (0-100) based on weather risks."""
  score = 0.0

  # Extract variables (defaults to safe values if missing)
  wind_speed = weather.get("wind_speed_10m", 0)  # km/h
  precipitation = weather.get("precipitation", 0)  # mm
  visibility = weather.get("visibility", 10000)  # meters

  # 1. Wind Hazard (High crosswinds on mountain passes)
  if wind_speed > 40:
    score += 40
  elif wind_speed > 25:
    score += 20

  # 2. Precipitation/Rain Hazard (Slip risk / hydroplaning)
  if precipitation > 10:
    score += 40
  elif precipitation > 2:
    score += 20

  # 3. Visibility / Fog Hazard (Reduced reaction time)
  if visibility < 1000:  # Dense fog
    score += 30
  elif visibility < 4000:  # Moderate mist/fog
    score += 15

  return min(score, 100.0)


# 2. Query Open-Meteo Free Weather API for each checkpoint
for cp in ROUTE_CHECKPOINTS:
  url = (
      f"https://api.open-meteo.com/v1/forecast?latitude={cp['lat']}&longitude={cp['lon']}"
      "&current=temperature_2m,precipitation,weather_code,wind_speed_10m,visibility"
  )

  try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    current = data.get("current", {})

    score = calculate_friction_score(current)

    # Determine status level
    if score >= 50:
      status = "HIGH FRICTION / HAZARD"
    elif score >= 20:
      status = "MODERATE CAUTION"
    else:
      status = "CLEAR / NORMAL"

    checkpoint_reports.append({
        "Checkpoint": cp["name"],
        "Latitude": cp["lat"],
        "Longitude": cp["lon"],
        "Wind (km/h)": current.get("wind_speed_10m"),
        "Precipitation (mm)": current.get("precipitation"),
        "Visibility (m)": current.get("visibility"),
        "Friction Score": score,
        "Status": status,
    })

  except Exception as e:
    print(f"Error fetching data for {cp['name']}: {e}")

# 3. Convert to DataFrame & Print Report
df_report = pd.DataFrame(checkpoint_reports)
print("\n--- Supply Chain Environmental Friction Report ---")
print(df_report.to_string(index=False))

# Optional: Save report to CSV or HTML for your dashboard
df_report.to_csv("friction_report.csv", index=False)
