import numpy as np
# [TODO] save generation and consumption data to CSV for later use in ML model training

# Base load power pattern in Wh for each hour of the day
base_load_power = {
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

def get_load_power(variance=0.15):
    load_power = {}
    for time, base_value in base_load_power.items():
        # Add Gaussian random variation to base load
        noise = np.random.normal(0, base_value * variance)
        # Ensure load never goes negative
        load_power[time] = max(0.0, base_value + noise)
    
    return load_power

if __name__ == "__main__":
    # Example usage
    load_profile = get_load_power()
    for time, power in load_profile.items():
        print(f"{time}: {power:.2f} Wh")