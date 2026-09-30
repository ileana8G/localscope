import requests


INSSE_LOCALITIES_URL = (
    "https://webgis.insse.ro/servicii/rest/services/"
    "Operational/Localitati/MapServer/0/query"
)


def _centroid_from_rings(rings: list[list[list[float]]]) -> tuple[float, float] | None:
    if not rings:
        return None

    points = rings[0]
    if len(points) < 1:
        return None

    lon_sum = 0.0
    lat_sum = 0.0
    count = 0

    for point in points:
        if len(point) < 2:
            continue
        lon_sum += point[0]
        lat_sum += point[1]
        count += 1

    if count == 0:
        return None

    return lat_sum / count, lon_sum / count


def fetch_localities():
    all_features = []
    offset = 0
    page_size = 2000

    while True:
        params = {
            "where": "1=1",
            "outFields": "siruta,denumire,judet,siruta_sup,tiplocalitate,populatie",
            "returnGeometry": "true",
            "outSR": "4326",
            "resultOffset": offset,
            "resultRecordCount": page_size,
            "f": "json",
        }

        response = requests.get(
            INSSE_LOCALITIES_URL,
            params=params,
            timeout=60,
        )
        response.raise_for_status()

        data = response.json()
        features = data.get("features", [])

        for feature in features:
            geometry = feature.get("geometry") or {}
            rings = geometry.get("rings") or []
            centroid = _centroid_from_rings(rings)
            if centroid is not None:
                feature["latitude"], feature["longitude"] = centroid
            else:
                feature["latitude"] = None
                feature["longitude"] = None

        all_features.extend(features)

        if len(features) < page_size:
            break

        offset += page_size

    return all_features
