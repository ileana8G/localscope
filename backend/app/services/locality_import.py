from backend.app.connectors.insse import fetch_localities
from backend.app.db.database import SessionLocal
from backend.app.models.locality import Locality


def import_localities():
    features = fetch_localities()

    localities = [
        Locality(
            siruta=feature["attributes"]["siruta"],
            name=feature["attributes"]["denumire"],
            county=feature["attributes"]["judet"],
            siruta_sup=feature["attributes"]["siruta_sup"],
            locality_type=feature["attributes"]["tiplocalitate"],
            population=feature["attributes"]["populatie"],
        )
        for feature in features
    ]

    with SessionLocal() as db:
        db.add_all(localities)
        db.commit()

    return len(localities)