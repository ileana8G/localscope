import requests

EUROSTAT_STATS_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
)


def fetch_dataset(
    dataset_code: str,
    *,
    geo_level: str = "nuts3",
    filters: dict[str, str] | None = None,
    last_time_period: int = 10,
) -> dict:
    params: dict[str, str | int] = {
        "lang": "EN",
        "format": "JSON",
        "geoLevel": geo_level,
        "lastTimePeriod": last_time_period,
    }

    if filters:
        params.update(filters)

    response = requests.get(
        f"{EUROSTAT_STATS_URL}/{dataset_code}",
        params=params,
        timeout=90,
    )
    response.raise_for_status()
    return response.json()


def parse_jsonstat_observations(
    payload: dict,
    *,
    geo_prefix: str = "RO",
    nuts_level: int = 3,
) -> list[dict]:
    """Flatten JSON-stat 2.0 cube into observation rows for matching geo codes."""
    dimension = payload.get("dimension") or {}
    ids = payload.get("id") or []
    size = payload.get("size") or []
    values = payload.get("value") or {}

    if not ids or not size or not values:
        return []

    # NUTS1=3 chars (RO1), NUTS2=4 (RO11), NUTS3=5 (RO111)
    expected_geo_len = {1: 3, 2: 4, 3: 5}.get(nuts_level, 5)

    categories: dict[str, dict[str, int]] = {}

    for dim_id in ids:
        category = (dimension.get(dim_id) or {}).get("category") or {}
        index = category.get("index") or {}
        categories[dim_id] = index

    position_to_code: dict[str, dict[int, str]] = {}
    for dim_id, index in categories.items():
        position_to_code[dim_id] = {pos: code for code, pos in index.items()}

    strides: list[int] = [1] * len(size)
    for i in range(len(size) - 2, -1, -1):
        strides[i] = strides[i + 1] * size[i + 1]

    observations: list[dict] = []

    for flat_key, raw_value in values.items():
        if raw_value is None:
            continue

        try:
            flat_index = int(flat_key)
        except (TypeError, ValueError):
            continue

        coords: dict[str, str] = {}
        remaining = flat_index
        for dim_id, stride, dim_size in zip(ids, strides, size):
            pos = remaining // stride
            remaining = remaining % stride
            if pos >= dim_size:
                break
            code = position_to_code[dim_id].get(pos)
            if code is None:
                break
            coords[dim_id] = code
        else:
            geo = coords.get("geo")
            if not geo or not geo.startswith(geo_prefix):
                continue
            if len(geo) != expected_geo_len:
                continue

            time_period = coords.get("time") or coords.get("TIME_PERIOD")
            if not time_period:
                continue

            observations.append(
                {
                    "geo_code": geo,
                    "time_period": time_period,
                    "value": float(raw_value),
                    "dims": coords,
                }
            )

    return observations
