import numpy as np
import pandas as pd
import os

# Mean load power pattern in Wh for each hour of the day
mean_load_power = {
    "00:00": 0.5,      # Midnight - minimal load
    "01:00": 0.3,      # 1 AM - low load
    "02:00": 0.2,      # 2 AM - low load
    "03:00": 0.2,      # 3 AM - low load
    "04:00": 0.3,      # 4 AM - low load
    "05:00": 0.8,      # 5 AM - early morning loads start
    "06:00": 1.2,      # 6 AM - morning peak begins
    "07:00": 1.8,      # 7 AM - morning peak
    "08:00": 2.1,      # 8 AM - high morning load
    "09:00": 2.0,      # 9 AM - high load
    "10:00": 1.9,      # 10 AM - daytime load
    "11:00": 1.8,      # 11 AM - daytime load
    "12:00": 2.2,      # Noon - lunch time load
    "13:00": 2.3,      # 1 PM - afternoon load
    "14:00": 2.1,      # 2 PM - afternoon load
    "15:00": 2.0,      # 3 PM - afternoon load
    "16:00": 1.9,      # 4 PM - afternoon load
    "17:00": 2.5,      # 5 PM - early evening load
    "18:00": 3.2,      # 6 PM - evening peak (cooking)
    "19:00": 3.5,      # 7 PM - evening peak
    "20:00": 3.3,      # 8 PM - evening load
    "21:00": 2.8,      # 9 PM - late evening
    "22:00": 1.8,      # 10 PM - night load
    "23:00": 1.0,      # 11 PM - late night load
}

def get_load_power(variance=0.2):
    load_power = {}
    for time, mean_value in mean_load_power.items():
        noise = np.random.normal(0, mean_value * variance)
        load_power[time] = max(0.0, mean_value + noise)

    return load_power

def save_load_profile_to_csv(load_profile, filename="consumption_data.csv"):
    df = pd.DataFrame(list(load_profile.items()), columns=["Time", "Load_Power_W"])
    df.index = pd.Index([pd.Timestamp.now().date()] * len(df), name="Date")
    file_exists = os.path.exists(filename) and os.path.getsize(filename) > 0

    if file_exists and list(pd.read_csv(filename, nrows=0).columns) == ["Time", "Load_Power_W"]:
        existing_df = pd.read_csv(filename)
        existing_df.insert(0, "Date", pd.NA)
        existing_df.to_csv(filename, index=False)

    df.to_csv(filename, mode="a", header=not file_exists, index=True)
    print(f"Load profile saved to {filename}")

if __name__ == "__main__":
    load_profile = get_load_power()
    save_load_profile_to_csv(load_profile)
    for time, power in load_profile.items():
        print(f"{time}: {power:.2f} W")