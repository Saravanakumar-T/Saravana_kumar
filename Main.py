# Install necessary libraries (Uncomment if needed)
!pip install pandas pennylane numpy matplotlib plotly geopandas folium

# Import libraries
import pandas as pd
import pennylane as qml
from pennylane import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import geopandas as gpd
import folium
from google.colab import files
import datetime
import random

# Step 1: Upload and Load Dataset
uploaded = files.upload()  # Upload the file manually in Google Colab
file_path = list(uploaded.keys())[0]  # Automatically gets the uploaded file name
df = pd.read_csv(file_path)

# Step 2: Check and Fix Column Names
df.columns = df.columns.str.strip()  # Remove trailing spaces

# Expected columns
expected_columns = ["Date", "Time", "Location", "Traffic Density", "Weather Condition", 
                    "Temperature (°C)", "Alternate Route Available", "Latitude", "Longitude"]

for col in expected_columns:
    if col not in df.columns:
        raise KeyError(f"⚠ Column '{col}' not found in dataset. Please check formatting.")

# Step 3: Extract Required Data
locations = df["Location"].tolist()
traffic_density = df["Traffic Density"].tolist()
weather_conditions = df["Weather Condition"].tolist()
temperatures = df["Temperature (°C)"].tolist()
alternate_routes = df["Alternate Route Available"].tolist()
latitudes = df["Latitude"].tolist()
longitudes = df["Longitude"].tolist()

# Step 4: Get Real-Time System Time and Predict Next Hour
current_time = datetime.datetime.now()
next_hour_time = current_time + datetime.timedelta(hours=1)

# Function to estimate delay based on traffic density
def estimate_delay(traffic):
    if traffic == "High":
        return random.randint(15, 45)  # High traffic: 15 to 45 minutes delay
    elif traffic == "Medium":
        return random.randint(5, 15)   # Medium traffic: 5 to 15 minutes delay
    else:
        return random.randint(0, 5)    # Low traffic: 0 to 5 minutes delay

# Add estimated delay to dataset
df["Estimated Delay (Minutes)"] = df["Traffic Density"].apply(estimate_delay)

# Simulating predicted traffic & weather (for next hour)
def predict_traffic(traffic_now):
    return random.choice(["Low", "Medium", "High"]) if traffic_now == "High" else traffic_now

def predict_weather(weather_now):
    return random.choice(["Sunny", "Cloudy", "Rainy", "Foggy", "Stormy"])

df["Predicted Traffic"] = df["Traffic Density"].apply(predict_traffic)
df["Predicted Weather"] = df["Weather Condition"].apply(predict_weather)

# Step 5: Load India's Boundary (GeoJSON)
india_boundary = gpd.read_file("https://datahub.io/core/geo-countries/r/0.geojson")
india_boundary = india_boundary[india_boundary["ADMIN"] == "India"]

# Step 6: Create a Chennai Map with Boundaries
chennai_map = folium.Map(location=[13.0827, 80.2707], zoom_start=11, tiles="CartoDB Positron")

# Add India's boundary
folium.GeoJson(india_boundary, name="India Boundary", style_function=lambda x: {
    "fillColor": "none",
    "color": "black",
    "weight": 2
}).add_to(chennai_map)

# Step 7: Add Traffic Points with Live Time, Prediction, and Alternate Routes
for loc, lat, lon, traffic, weather, temp, alt_route, delay, pred_traffic, pred_weather in zip(
        df["Location"], df["Latitude"], df["Longitude"], df["Traffic Density"], 
        df["Weather Condition"], df["Temperature (°C)"], df["Alternate Route Available"], 
        df["Estimated Delay (Minutes)"], df["Predicted Traffic"], df["Predicted Weather"]):

    risk_level = "🔴 High Risk" if traffic == "High" else ("🟠 Medium Risk" if traffic == "Medium" else "🟢 Low Risk")
    alternate_route_info = f"<b>Alternate Route:</b> ✅ Available" if alt_route == "Yes" else "<b>Alternate Route:</b> ❌ Not Available"

    popup_text = f"""
    <b>Location:</b> {loc}<br>
    <b>Current Time:</b> {current_time.strftime("%Y-%m-%d %H:%M:%S")}<br>
    <b>Current Traffic:</b> {traffic}<br>
    <b>Weather:</b> {weather}<br>
    <b>Temperature:</b> {temp}°C<br>
    <b>Risk Level:</b> {risk_level}<br>
    <b>Estimated Delay:</b> ⏳ {delay} minutes<br><br>

    <b>📌 Predicted Traffic in 1 Hour:</b> {pred_traffic}<br>
    <b>📌 Predicted Weather in 1 Hour:</b> {pred_weather}<br>
    {alternate_route_info}
    """

    marker_color = "red" if traffic == "High" else ("orange" if traffic == "Medium" else "green")
    
    folium.Marker(
        location=[lat, lon],
        popup=popup_text,
        icon=folium.Icon(color=marker_color)
    ).add_to(chennai_map)

# Step 8: Add a Legend for Traffic Levels
legend_html = """
<div style="position: fixed; bottom: 50px; left: 50px; width: 250px; height: 180px;
background-color: white; z-index: 9999; padding: 10px; border-radius: 5px;
box-shadow: 2px 2px 5px grey; font-size:14px;">
<b>Traffic Levels</b><br>
🟢 <span style="color:green;">Low Traffic</span><br>
🟠 <span style="color:orange;">Medium Traffic</span><br>
🔴 <span style="color:red;">High Traffic</span><br><br>
<b>📌 Predictions:</b><br>
📅 Traffic & Weather for next hour<br>
⏳ Estimated delay time added!<br>
</div>
"""
chennai_map.get_root().html.add_child(folium.Element(legend_html))

# Step 9: Display the Chennai Map
from IPython.display import display
display(chennai_map)

# Step 10: Save & Download the Map
chennai_map.save("chennai_traffic_map.html")
files.download("chennai_traffic_map.html")

# Step 11: Summary of High Traffic Areas
high_traffic_summary = df[df["Traffic Density"] == "High"][["Location", "Estimated Delay (Minutes)"]].groupby("Location").mean().reset_index()

summary_text = "\n🚦 **High Traffic Areas & Estimated Delays:**\n"
for _, row in high_traffic_summary.iterrows():
    summary_text += f"📍 {row['Location']}: ⏳ ~{int(row['Estimated Delay (Minutes)'])} min delay\n"

print(summary_text)
