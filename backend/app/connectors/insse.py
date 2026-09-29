import requests


INSSE_LOCALITIES_URL = (
    "https://webgis.insse.ro/servicii/rest/services/"
    "Operational/Localitati/MapServer/0/query"
)


def fetch_localities():
    all_features = []
    offset = 0
    page_size = 2000

    while True:
        params = {
            "where": "1=1",
            "outFields": "siruta,denumire,judet,siruta_sup,tiplocalitate,populatie",
            "returnGeometry": "false",
            "resultOffset": offset,
            "resultRecordCount": page_size,
            "f": "json",
        }

        response = requests.get(
            INSSE_LOCALITIES_URL,
            params=params,
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        features = data.get("features", [])

        all_features.extend(features)

        if len(features) < page_size:
            break

        offset += page_size

    return all_features