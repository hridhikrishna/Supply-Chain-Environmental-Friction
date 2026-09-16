import os
import folium
import pandas as pd
import requests

# 1. Define Key Logistics Checkpoints along the Freight Corridor
ROUTE_CHECKPOINTS = [
    {"name": "Thamarassery Churam (Hairpin 9)", "lat": 11.4885, "lon": 76.0822},
    {"name": "Vythiri Pass Summit", "lat": 11.5515, "lon": 76.0448},
    {"name": "Kalpetta Highway Junction", "lat": 11.6054, "lon": 76.0830},
    {"name": "Sulthan Bathery Foothills", "lat": 11.6667, "lon": 76.2667},
]

print("Evaluating environmental friction scores for transit checkpoints...")

checkpoint_reports = []


def calculate_friction_score(weather):
  """Calculates an environmental friction score (0-100) based on weather risks."""
  score = 0.0
  wind_speed = weather.get("wind_speed_10m", 0)
  precipitation = weather.get("precipitation", 0)
  visibility = weather.get("visibility", 10000)

  if wind_speed > 40:
    score += 40
  elif wind_speed > 25:
    score += 20

  if precipitation > 10:
    score += 40
  elif precipitation > 2:
    score += 20

  if visibility < 1000:
    score += 30
  elif visibility < 4000:
    score += 15

  return min(score, 100.0)


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

    if score >= 50:
      status = "HIGH FRICTION / HAZARD"
      color = "red"
    elif score >= 20:
      status = "MODERATE CAUTION"
      color = "orange"
    else:
      status = "CLEAR / NORMAL"
      color = "green"

    checkpoint_reports.append({
        "name": cp["name"],
        "lat": cp["lat"],
        "lon": cp["lon"],
        "wind": current.get("wind_speed_10m", 0),
        "precip": current.get("precipitation", 0),
        "visibility": current.get("visibility", 10000),
        "score": score,
        "status": status,
        "color": color,
    })
  except Exception as e:
    print(f"Error fetching data for {cp['name']}: {e}")

# 2. Generate Interactive Map
supply_map = folium.Map(location=[11.5515, 76.0448], zoom_start=11)

folium.TileLayer(
    tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    attr="OpenStreetMap",
    name="Street Map",
).add_to(supply_map)

for pt in checkpoint_reports:
  popup_text = f"""
        <b>Checkpoint:</b> {pt['name']}<br>
        <b>Status:</b> <span style="color:{pt['color']}; font-weight:bold;">{pt['status']}</span><br>
        <b>Friction Score:</b> {pt['score']}/100<br>
        <b>Wind Speed:</b> {pt['wind']} km/h<br>
        <b>Precipitation:</b> {pt['precip']} mm<br>
        <b>Visibility:</b> {pt['visibility']} m
    """
  folium.Marker(
      location=[pt["lat"], pt["lon"]],
      popup=folium.Popup(popup_text, max_width=300),
      icon=folium.Icon(color=pt["color"], icon="info-sign"),
  ).add_to(supply_map)

# Save map and historical log
supply_map.save("index.html")
pd.DataFrame(checkpoint_reports).to_csv(
    "logistics_friction_log.csv", index=False
)
print("Generated fresh supply chain environmental friction map & log.")
