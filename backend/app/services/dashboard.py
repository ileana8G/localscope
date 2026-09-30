from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.connectors.eea_aq import find_nearest_station, stations_for_nuts3
from backend.app.connectors.open_meteo import fetch_era5_climate, fetch_forecast
from backend.app.models.county import County
from backend.app.models.indicator import Indicator, IndicatorValue
from backend.app.models.locality import Locality


def _indicator_series_for_geo_codes(
    db: Session,
    geo_codes: list[str],
) -> list[dict]:
    indicators = db.scalars(
        select(Indicator).where(Indicator.source == "eurostat")
    ).all()

    series = []
    for indicator in indicators:
        values = []
        matched_geo = None
        for geo_code in geo_codes:
            values = db.scalars(
                select(IndicatorValue)
                .where(
                    IndicatorValue.indicator_id == indicator.id,
                    IndicatorValue.geo_code == geo_code,
                )
                .order_by(IndicatorValue.time_period.desc())
                .limit(15)
            ).all()
            if values:
                matched_geo = geo_code
                break

        if not values:
            continue

        series.append(
            {
                "code": indicator.code,
                "label": indicator.label,
                "unit": indicator.unit,
                "source": indicator.source,
                "geo_level": indicator.geo_level,
                "geo_code": matched_geo,
                "theme": indicator.theme,
                "values": [
                    {"time_period": row.time_period, "value": row.value}
                    for row in reversed(values)
                ],
            }
        )

    return series


def _indicator_series_for_geo(db: Session, geo_code: str) -> list[dict]:
    return _indicator_series_for_geo_codes(db, [geo_code])


def _weather_payload(latitude: float | None, longitude: float | None) -> dict | None:
    if latitude is None or longitude is None:
        return None

    try:
        forecast = fetch_forecast(latitude, longitude)
        climate = fetch_era5_climate(latitude, longitude)
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}

    return {
        "source": "open_meteo",
        "forecast": {
            "current": forecast.get("current"),
            "daily": forecast.get("daily"),
            "units": {
                "current": forecast.get("current_units"),
                "daily": forecast.get("daily_units"),
            },
        },
        "climate": climate,
    }


def _air_quality_for_point(
    latitude: float | None,
    longitude: float | None,
) -> dict:
    if latitude is None or longitude is None:
        return {"source": "eea", "station": None, "stations": []}

    station = find_nearest_station(latitude, longitude)
    return {
        "source": "eea",
        "station": station,
        "stations": [station] if station else [],
        "note": (
            "Măsurători de la stația EEA cea mai apropiată. "
            "Valorile live detaliate pot fi sincronizate separat."
            if station
            else "Nu există stație EEA în rază rezonabilă."
        ),
    }


def build_locality_dashboard(db: Session, siruta: int) -> dict | None:
    locality = db.scalar(select(Locality).where(Locality.siruta == siruta))
    if locality is None:
        return None

    county = None
    if locality.county_id is not None:
        county = db.get(County, locality.county_id)

    stats = []
    if county is not None:
        stats = _indicator_series_for_geo_codes(
            db,
            [county.nuts3, county.nuts2],
        )

    return {
        "place": {
            "type": "locality",
            "id": locality.id,
            "siruta": locality.siruta,
            "name": locality.name,
            "county": locality.county,
            "county_nuts3": county.nuts3 if county else None,
            "locality_type": locality.locality_type,
            "population": locality.population,
            "latitude": locality.latitude,
            "longitude": locality.longitude,
        },
        "stats": stats,
        "weather": _weather_payload(locality.latitude, locality.longitude),
        "air_quality": _air_quality_for_point(
            locality.latitude,
            locality.longitude,
        ),
    }


def build_county_dashboard(db: Session, nuts3: str) -> dict | None:
    county = db.scalar(select(County).where(County.nuts3 == nuts3.upper()))
    if county is None:
        return None

    return {
        "place": {
            "type": "county",
            "id": county.id,
            "name": county.name,
            "nuts3": county.nuts3,
            "nuts2": county.nuts2,
            "latitude": county.latitude,
            "longitude": county.longitude,
        },
        "stats": _indicator_series_for_geo_codes(
            db,
            [county.nuts3, county.nuts2],
        ),
        "weather": _weather_payload(county.latitude, county.longitude),
        "air_quality": {
            "source": "eea",
            "station": None,
            "stations": stations_for_nuts3(county.nuts3),
            "note": "Stații EEA din județ (NUTS3).",
        },
    }
