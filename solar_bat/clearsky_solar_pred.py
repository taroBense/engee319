import matplotlib.pyplot as plt
import pandas as pd
import pvlib
from pvlib.location import Location
import requests
import numpy as np
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

# Hamilton Info + Time of prediction period
site = Location(-37.7870, 175.2793, tz="Pacific/Auckland", altitude=40)
times = pd.date_range(
    "2026-08-30 00:00", "2026-09-06 23:00", freq="15min", tz="Pacific/Auckland"
)

# Panel Config (e.g., 30° tilt, North-facing / 0° azimuth for Southern Hemisphere)
surface_tilt = 30
surface_azimuth = 0  # North = 0° in pvlib

# Get Solar Position & Clear-Sky Data
solpos = site.get_solarposition(times)
clearsky = site.get_clearsky(times, model="ineichen")

# Calculate Plane of Array (POA) Irradiance
poa_irrad = pvlib.irradiance.get_total_irradiance(
    surface_tilt=surface_tilt,
    surface_azimuth=surface_azimuth,
    solar_zenith=solpos["apparent_zenith"],
    solar_azimuth=solpos["azimuth"],
    dni=clearsky["dni"],
    ghi=clearsky["ghi"],
    dhi=clearsky["dhi"],
)

# Power Output Estimate
array_kw_rating = 0.005
power_output_watts = poa_irrad["poa_global"] * array_kw_rating

# Controller state control
df = pd.DataFrame(
    {"POA_Irradiance": poa_irrad["poa_global"], "Estimated_W": power_output_watts}
)


def get_weather_forecast(lat, lon, days=30):
    """
    Fetch weather forecast data from Open-Meteo API
    """
    try:
        url = "https://archive-api.open-meteo.com/v1/archive"

        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": "2026-08-30",
            "end_date": "2026-09-06",
            "hourly": ["cloud_cover", "precipitation", "weather_code"],
            "timezone": "Pacific/Auckland",
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Create DataFrame from hourly data
        weather_df = pd.DataFrame(
            {
                "time": pd.to_datetime(data["hourly"]["time"]),
                "cloud_cover": data["hourly"]["cloud_cover"],
                "precipitation": data["hourly"]["precipitation"],
            }
        )

        weather_df.set_index("time", inplace=True)
        return weather_df

    except Exception as e:
        print(f"Warning: Could not fetch weather data: {e}")
        print("Using synthetic weather data instead...")
        return generate_synthetic_weather(lat, lon)


def generate_synthetic_weather(lat, lon, num_days=7):
    """
    Generate synthetic but realistic weather data for solar prediction.
    Based on typical weather patterns for Hamilton, NZ (Spring weather).
    """
    dates = pd.date_range(
        "2026-08-30", periods=num_days * 24, freq="h", tz="Pacific/Auckland"
    )

    # Cloud cover pattern (more clouds in morning/evening)
    hour_of_day = dates.hour
    cloud_cover = 40 + 30 * np.sin((hour_of_day - 6) * np.pi / 12)
    cloud_cover = np.clip(cloud_cover, 5, 90)

    # Add daily variation (some days cloudier than others)
    day_num = np.arange(len(dates))
    daily_pattern = 15 * np.sin(day_num * np.pi / 7)  # Weekly pattern
    cloud_cover = cloud_cover + daily_pattern
    cloud_cover = np.clip(cloud_cover, 0, 100)

    # Precipitation (occasional rain)
    precipitation = np.zeros(len(dates))
    rain_days = np.random.choice(num_days, size=max(1, num_days // 7), replace=False)
    for rain_day in rain_days:
        rain_start = rain_day * 24 + np.random.randint(6, 18)
        rain_duration = np.random.randint(2, 6)
        if rain_start + rain_duration < len(dates):
            precipitation[rain_start : rain_start + rain_duration] = np.random.uniform(
                0.5, 3, rain_duration
            )

    weather_df = pd.DataFrame(
        {
            "cloud_cover": cloud_cover,
            "precipitation": precipitation,
        },
        index=dates,
    )

    return weather_df


def apply_weather_adjustments(irradiance, weather_df):
    """
    Apply weather-based adjustments to solar irradiance predictions.
    - Cloud cover reduces direct irradiance
    - Precipitation cleans panels (improves efficiency)
    """
    adjusted_irradiance = irradiance.copy()

    # Cloud cover adjustment (0-100% -> 1.0-0.1 multiplier)
    cloud_factor = 1.0 - (weather_df["cloud_cover"] / 100 * 0.85)
    cloud_factor = np.maximum(cloud_factor, 0.05)  # Minimum 5% on very cloudy days

    # Soiling factor (precipitation cleans panels, dust increases over time)
    soiling = (
        0.98 - (np.arange(len(weather_df)) / len(weather_df)) * 0.05
    )  # Gradual soiling
    rain_factor = (
        1.0 + (weather_df["precipitation"] > 0).astype(float) * 0.02
    )  # Cleaning effect

    # Combine all factors
    total_factor = cloud_factor * soiling * rain_factor
    adjusted_irradiance = irradiance * total_factor

    return adjusted_irradiance


# Fetch/Generate weather data
print("Fetching weather data...")
weather_data = get_weather_forecast(site.latitude, site.longitude)

# Resample weather data to match 15-min solar data resolution
weather_resampled = weather_data.resample("15min").interpolate(method="linear")

# Apply weather adjustments to irradiance
adjusted_poa_irrad = apply_weather_adjustments(
    poa_irrad["poa_global"], weather_resampled
)

# Recalculate power output with weather adjustments
adjusted_power_watts = adjusted_poa_irrad * array_kw_rating

# Add weather data to DataFrame
df["Cloud_Cover_%"] = weather_resampled["cloud_cover"]
df["Precipitation_mm"] = weather_resampled["precipitation"]
df["Adjusted_POA_Irradiance"] = adjusted_poa_irrad
df["Adjusted_Power_W"] = adjusted_power_watts
df["Weather_Factor"] = adjusted_poa_irrad / (
    poa_irrad["poa_global"] + 1e-6
)

print(f"Weather prediction added with {len(weather_data)} hourly records")
print(f"\nWeather Data Summary:")
print(weather_data.describe())
print(f"\nSolar + Weather Prediction Summary:")
print(df.describe())

# Create multi-panel visualization
fig, axes = plt.subplots(3, 1, figsize=(14, 10))
fig.suptitle(
    "Solar Energy Prediction with Weather Data - Hamilton, NZ (September 2026)",
    fontsize=14,
    fontweight="bold",
)

# Plot 1: Power Output (Clear-sky vs Weather-adjusted)
ax = axes[0]
df.index.name = "Time"
ax.plot(
    df.index, df["Estimated_W"] / 1000, label="Clear-Sky Power", linewidth=2, alpha=0.7
)
ax.plot(
    df.index,
    df["Adjusted_Power_W"] / 1000,
    label="Weather-Adjusted Power",
    linewidth=2,
    color="orange",
)
ax.fill_between(df.index, 0, df["Adjusted_Power_W"] / 1000, alpha=0.2, color="orange")
ax.set_ylabel("Power Output (kW)")
ax.set_title("Solar Panel Power Output with Weather Adjustments")
ax.legend(loc="upper right")
ax.grid(True, alpha=0.3)

# Plot 2: Cloud Cover & Precipitation
ax = axes[1]
ax2 = ax.twinx()
ax.bar(
    df.index,
    df["Cloud_Cover_%"],
    label="Cloud Cover",
    alpha=0.5,
    color="blue",
    width=0.01,
)
ax2.bar(
    df.index,
    df["Precipitation_mm"],
    label="Precipitation",
    alpha=0.5,
    color="cyan",
    width=0.01,
)
ax.set_ylabel("Cloud Cover (%)", color="blue")
ax2.set_ylabel("Precipitation (mm)", color="cyan")
ax.set_title("Weather Conditions")
ax.tick_params(axis="y", labelcolor="blue")
ax2.tick_params(axis="y", labelcolor="cyan")
ax.grid(True, alpha=0.3)

# Plot 3: Weather Impact Factor
ax = axes[2]
ax.plot(
    df.index,
    df["Weather_Factor"],
    label="Weather Adjustment Factor",
    linewidth=2,
    color="purple",
)
ax.axhline(y=1.0, color="black", linestyle="--", linewidth=1, alpha=0.5)
ax.fill_between(df.index, 0, df["Weather_Factor"], alpha=0.2, color="purple")
ax.set_ylabel("Adjustment Factor")
ax.set_xlabel("Date/Time")
ax.set_title("Weather Impact on Solar Irradiance (1.0 = Clear Sky)")
ax.set_ylim(0, 1.1)
ax.legend(loc="upper right")
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Daily summary
print("\n" + "=" * 60)
print("DAILY WEATHER & SOLAR PREDICTION SUMMARY")
print("=" * 60)
daily_summary = df.resample("D").agg(
    {
        "Estimated_W": "mean",
        "Adjusted_Power_W": "mean",
        "Cloud_Cover_%": "mean",
        "Precipitation_mm": "sum",
    }
)
print(daily_summary)
