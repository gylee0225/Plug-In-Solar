"""SI units: degrees, W/m², °C, m/s, W, kWh; azimuth clockwise from north."""
import math
import numpy as np
import pandas as pd
import pvlib


def number(value, name, low=None, high=None):
    value = float(value)
    if not math.isfinite(value) or (low is not None and value < low) or (high is not None and value > high):
        raise ValueError("{} must be finite and within [{}, {}].".format(name, low, high))
    return value


def location(latitude, longitude, timezone, altitude_m=0):
    lat = number(latitude, "latitude", -90, 90)
    lon = number(longitude, "longitude", -180, 180)
    altitude = number(altitude_m, "altitude_m")
    if not timezone:
        raise ValueError("Provide a timezone, e.g. Europe/Berlin.")
    return pvlib.location.Location(lat, lon, tz=str(timezone), altitude=altitude)


def times_for(site, start, end, step_minutes=60):
    step = number(step_minutes, "step_minutes", 1, 1440)
    def local(value):
        stamp = pd.Timestamp(value)
        return stamp.tz_localize(site.tz) if stamp.tzinfo is None else stamp.tz_convert(site.tz)
    first, last = local(start), local(end)
    if last <= first:
        raise ValueError("End must be after start (end is exclusive).")
    if (last-first).total_seconds() / (step*60) > 200000:
        raise ValueError("Use at most 200,000 samples per run.")
    return pd.date_range(first, last, freq=pd.Timedelta(minutes=step), inclusive="left")


def clear_sky(site, start, end, step_minutes=60):
    """Synthetic clear-sky irradiance, not measured weather or a yield forecast."""
    return site.get_clearsky(times_for(site, start, end, step_minutes))


def sun_position(site, timestamps):
    index = pd.DatetimeIndex(timestamps)
    if index.empty or index.tz is None or index.hasnans:
        raise ValueError("Provide nonempty timezone-aware timestamps.")
    return site.get_solarposition(index)


def orientation(x, y, z, north_deg=0):
    """Model +Y is north at 0°. North rotation is clockwise toward +X.

    Supply the front-face normal; no silent flipping of downward normals.
    """
    x, y, z = [number(v, "normal") for v in (x, y, z)]
    north = number(north_deg, "north_deg")
    length = math.sqrt(x*x+y*y+z*z)
    if length == 0:
        raise ValueError("Panel normal cannot be zero.")
    tilt = math.degrees(math.acos(max(-1, min(1, z/length))))
    azimuth = (math.degrees(math.atan2(x, y))-north) % 360
    return tilt, azimuth


def irradiance(weather, solar, tilt_deg, azimuth_deg, albedo=0.2):
    tilt = number(tilt_deg, "tilt_deg", 0, 180)
    azimuth = number(azimuth_deg, "azimuth_deg", 0, 360)
    ground = number(albedo, "albedo", 0, 1)
    if not weather.index.equals(solar.index):
        raise ValueError("Weather and sun timestamps must match exactly.")
    for col in ("ghi", "dni", "dhi"):
        if col not in weather or not np.isfinite(weather[col]).all() or (weather[col] < 0).any():
            raise ValueError("Weather requires finite nonnegative ghi, dni and dhi in W/m².")
    return pvlib.irradiance.get_total_irradiance(
        tilt, azimuth, solar.apparent_zenith, solar.azimuth,
        weather.dni, weather.ghi, weather.dhi, albedo=ground, model="isotropic")


def pv_power(poa, dc_capacity_w=800, ac_limit_w=800, air_temp_c=20, wind_m_s=1, gamma_pdc=-0.004, losses_pct=14):
    """Simplified PVWatts DC + inverter; Faiman temperature, no shading model.

    ac_limit_w is rated AC power, distinct from inverter DC reference power.
    Ambient temperature and wind are constant scenario inputs in this starter.
    """
    dc = number(dc_capacity_w, "dc_capacity_w", 0.001)
    ac = number(ac_limit_w, "ac_limit_w", 0.001)
    temp = number(air_temp_c, "air_temp_c")
    wind = number(wind_m_s, "wind_m_s", 0)
    gamma = number(gamma_pdc, "gamma_pdc", -0.02, 0)
    losses = number(losses_pct, "losses_pct", 0, 100)
    if not isinstance(poa, pd.Series) or poa.empty or not np.isfinite(poa).all() or (poa < 0).any():
        raise ValueError("Provide a nonempty finite nonnegative POA irradiance Series.")
    cell = pvlib.temperature.faiman(poa, temp, wind)
    pdc = pvlib.pvsystem.pvwatts_dc(poa, cell, dc, gamma).clip(lower=0)*(1-losses/100)
    pac = pvlib.inverter.pvwatts(pdc, pdc0=ac/0.96, eta_inv_nom=0.96)
    return pd.DataFrame({"cell_temp_c": cell, "dc_w": pdc, "ac_w": pac}, index=poa.index)


def energy_kwh(power_w, step_hours):
    """Rectangle integration: each value represents one interval of step_hours.

    Explicit interval duration includes the last sample and allows one sample.
    Irregular time series are rejected; values are interval-average power.
    """
    hours = number(step_hours, "step_hours", 0.000001)
    if not isinstance(power_w, pd.Series) or power_w.empty:
        raise ValueError("Provide a nonempty time-indexed power Series.")
    index = power_w.index
    if not isinstance(index, pd.DatetimeIndex) or index.tz is None or index.hasnans:
        raise ValueError("Power timestamps must be timezone-aware.")
    if not np.isfinite(power_w).all() or (power_w < 0).any():
        raise ValueError("Power must be finite and nonnegative.")
    if len(index)>1 and not np.allclose(np.diff(index.asi8)/3.6e12, hours):
        raise ValueError("Timestamp spacing must match step_hours, without gaps or duplicates.")
    return float(power_w.sum()*hours/1000)
