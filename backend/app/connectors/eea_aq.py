import csv
import io
import math
import zipfile

import requests
from sqlalchemy import select

from backend.app.db.database import SessionLocal
from backend.app.models.aq_station import AqStation
from backend.app.models.county import County

EEA_METADATA_URL = (
    "https://discomap.eea.europa.eu/App/AQViewer/download"
    "?fqn=Airquality_Dissem.b2g.measurements&f=csv"
)


def _haversine_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return 2 * radius * math.asin(math.sqrt(a))


def _row_get(row: dict, *candidates: str) -> str:
    for key in candidates:
        if key in row and row[key] not in (None, ""):
            return str(row[key]).strip()
    lower_map = {k.lower(): k for k in row}
    for key in candidates:
        actual = lower_map.get(key.lower())
        if actual and row[actual] not in (None, ""):
            return str(row[actual]).strip()
    return ""


def fetch_romania_station_rows() -> list[dict]:
    response = requests.get(EEA_METADATA_URL, timeout=180)
    response.raise_for_status()

    content = response.content

    if content[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            names = archive.namelist()
            csv_name = next(
                (name for name in names if name.lower().endswith(".csv")),
                names[0],
            )
            text = archive.read(csv_name).decode("utf-8", errors="replace")
    else:
        text = content.decode("utf-8", errors="replace")

    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for row in reader:
        country = _row_get(row, "Country", "Countrycode", "CountryCode").lower()
        if country not in {"romania", "ro"}:
            continue
        rows.append(row)
    return rows


def sync_aq_stations() -> dict:
    rows = fetch_romania_station_rows()

    with SessionLocal() as db:
        counties_by_nuts3 = {
            county.nuts3: county
            for county in db.scalars(select(County)).all()
        }
        existing = {
            station.eoi_code: station
            for station in db.scalars(select(AqStation)).all()
        }

        created = 0
        updated = 0
        seen: set[str] = set()

        for row in rows:
            eoi = _row_get(
                row,
                "Air Quality Station EoI Code",
                "AirQualityStationEoICode",
                "AirQualityStationEoiCode",
            )
            if not eoi or eoi in seen:
                continue

            lat_raw = _row_get(row, "Latitude")
            lon_raw = _row_get(row, "Longitude")
            try:
                latitude = float(lat_raw)
                longitude = float(lon_raw)
            except ValueError:
                continue

            county = None
            nuts3 = None

            # Assign county by nearest county centroid (reliable for RO).
            best_distance = float("inf")
            for county_obj in counties_by_nuts3.values():
                if county_obj.latitude is None or county_obj.longitude is None:
                    continue
                distance = _haversine_km(
                    latitude,
                    longitude,
                    county_obj.latitude,
                    county_obj.longitude,
                )
                if distance < best_distance:
                    best_distance = distance
                    county = county_obj
                    nuts3 = county_obj.nuts3

            name = _row_get(
                row,
                "Air Quality Station Name",
                "AirQualityStationName",
                "StationName",
            ) or eoi
            pollutant = _row_get(row, "Air Pollutant", "AirPollutant", "Pollutant")

            station = existing.get(eoi)
            if station is None:
                station = AqStation(
                    eoi_code=eoi,
                    name=name,
                    latitude=latitude,
                    longitude=longitude,
                    county_id=county.id if county else None,
                    nuts3=nuts3,
                    pollutants=pollutant or None,
                )
                db.add(station)
                created += 1
            else:
                station.name = name
                station.latitude = latitude
                station.longitude = longitude
                station.county_id = county.id if county else station.county_id
                station.nuts3 = nuts3 or station.nuts3
                if pollutant:
                    current = set((station.pollutants or "").split(","))
                    current.discard("")
                    current.add(pollutant)
                    station.pollutants = ",".join(sorted(current))
                updated += 1

            seen.add(eoi)

        db.commit()

    return {"created": created, "updated": updated, "total_rows": len(rows)}


def find_nearest_station(
    latitude: float,
    longitude: float,
    *,
    max_distance_km: float = 50.0,
) -> dict | None:
    with SessionLocal() as db:
        stations = db.scalars(select(AqStation)).all()

    if not stations:
        return None

    best = None
    best_distance = float("inf")
    for station in stations:
        distance = _haversine_km(
            latitude,
            longitude,
            station.latitude,
            station.longitude,
        )
        if distance < best_distance:
            best_distance = distance
            best = station

    if best is None or best_distance > max_distance_km:
        return None

    return {
        "eoi_code": best.eoi_code,
        "name": best.name,
        "latitude": best.latitude,
        "longitude": best.longitude,
        "nuts3": best.nuts3,
        "pollutants": best.pollutants,
        "distance_km": round(best_distance, 2),
    }


def stations_for_nuts3(nuts3: str) -> list[dict]:
    with SessionLocal() as db:
        stations = db.scalars(
            select(AqStation).where(AqStation.nuts3 == nuts3)
        ).all()

    return [
        {
            "eoi_code": station.eoi_code,
            "name": station.name,
            "latitude": station.latitude,
            "longitude": station.longitude,
            "nuts3": station.nuts3,
            "pollutants": station.pollutants,
        }
        for station in stations
    ]
