from datetime import date, timedelta

import requests

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


def fetch_forecast(latitude: float, longitude: float) -> dict:
    response = requests.get(
        FORECAST_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "timezone": "Europe/Bucharest",
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "daily": (
                "weather_code,temperature_2m_max,temperature_2m_min,"
                "precipitation_sum"
            ),
            "forecast_days": 7,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def fetch_era5_climate(
    latitude: float,
    longitude: float,
    *,
    months: int = 12,
) -> dict:
    end = date.today().replace(day=1) - timedelta(days=1)
    start = (end.replace(day=1) - timedelta(days=months * 31)).replace(day=1)

    response = requests.get(
        ARCHIVE_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "daily": "temperature_2m_mean,precipitation_sum",
            "timezone": "Europe/Bucharest",
            "models": "era5",
        },
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()

    daily = payload.get("daily") or {}
    times = daily.get("time") or []
    temps = daily.get("temperature_2m_mean") or []
    precip = daily.get("precipitation_sum") or []

    monthly: dict[str, dict[str, list[float]]] = {}
    for time_value, temp, rain in zip(times, temps, precip):
        month_key = time_value[:7]
        bucket = monthly.setdefault(month_key, {"temp": [], "precip": []})
        if temp is not None:
            bucket["temp"].append(temp)
        if rain is not None:
            bucket["precip"].append(rain)

    climate = []
    for month_key in sorted(monthly):
        bucket = monthly[month_key]
        climate.append(
            {
                "month": month_key,
                "avg_temperature_c": (
                    round(sum(bucket["temp"]) / len(bucket["temp"]), 2)
                    if bucket["temp"]
                    else None
                ),
                "total_precipitation_mm": (
                    round(sum(bucket["precip"]), 1)
                    if bucket["precip"]
                    else None
                ),
            }
        )

    return {
        "source": "era5",
        "provider": "open-meteo",
        "monthly": climate,
    }
