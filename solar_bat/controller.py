import clearsky_solar_pred
import load

generation = clearsky_solar_pred.get_power_output()
consumption = load.get_load_power()