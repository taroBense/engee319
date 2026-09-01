import matplotlib.pyplot as plt
import pandas as pd
import pvlib
from pvlib.location import Location

# Hamilton Info + Time of prediction period
site = Location(
    -37.7870, 175.2793, tz="Pacific/Auckland", altitude=40
)
times = pd.date_range(
    "2026-09-01 00:00", "2026-09-30 23:00", freq="15min", tz="Pacific/Auckland"
)

# Panel Configuration (e.g., 30° tilt, North-facing / 0° azimuth for Southern Hemisphere)
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
array_kw_rating = 0.012
power_output_watts = poa_irrad["poa_global"] * array_kw_rating

# Controller state control
df = pd.DataFrame(
    {"POA_Irradiance": poa_irrad["poa_global"], "Estimated_W": power_output_watts}
)
# df["Action"] = "Grid / Battery"
# df.loc[df["Estimated_W"] > 1500, "Action"] = "Run Heavy Appliances / Charge Battery"

# Plots
fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

axes[0].plot(df.index, df["POA_Irradiance"], color="tab:orange", linewidth=1.5)
axes[0].set_title("Solar POA Irradiance Over September")
axes[0].set_ylabel("Irradiance (W/m²)")
axes[0].grid(True, alpha=0.3)

axes[1].plot(df.index, df["Estimated_W"], color="tab:blue", linewidth=1.5)
axes[1].axhline(1500, color="tab:red", linestyle="--", linewidth=1.2, label="Action threshold")
axes[1].set_title("Estimated Power Output")
axes[1].set_ylabel("Power (W)")
axes[1].set_xlabel("Time")
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Highlight high-output periods
peak_mask = df["Estimated_W"] > 1500
if peak_mask.any():
    for idx in df.index[peak_mask]:
        axes[1].axvline(idx, color="green", alpha=0.1, linewidth=4)

fig.tight_layout()
plt.savefig("solar_prediction_graphs.png", dpi=200)
plt.show()

print(df[df["Estimated_W"] > 0].head(10))
