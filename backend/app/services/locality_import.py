from sqlalchemy import select

from backend.app.connectors.insse import fetch_localities
from backend.app.db.database import SessionLocal
from backend.app.models.county import County
from backend.app.models.locality import Locality


def import_localities():
    features = fetch_localities()

    with SessionLocal() as db:
        counties_by_name = {
            county.name: county
            for county in db.scalars(select(County)).all()
        }

        existing = {
            locality.siruta: locality
            for locality in db.scalars(select(Locality)).all()
        }

        created = 0
        updated = 0

        for feature in features:
            attributes = feature["attributes"]
            siruta = attributes["siruta"]
            county_name = (attributes.get("judet") or "").upper()
            county = counties_by_name.get(county_name)

            values = {
                "name": attributes["denumire"],
                "county": county_name,
                "county_id": county.id if county else None,
                "siruta_sup": attributes.get("siruta_sup"),
                "locality_type": attributes.get("tiplocalitate"),
                "population": attributes.get("populatie"),
                "latitude": feature.get("latitude"),
                "longitude": feature.get("longitude"),
            }

            locality = existing.get(siruta)
            if locality is None:
                locality = Locality(siruta=siruta, **values)
                db.add(locality)
                created += 1
            else:
                for key, value in values.items():
                    setattr(locality, key, value)
                updated += 1

        db.commit()

    return {"created": created, "updated": updated, "total": len(features)}
