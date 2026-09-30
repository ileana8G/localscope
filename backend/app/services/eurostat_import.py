from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from backend.app.connectors.eurostat import (
    fetch_dataset,
    parse_jsonstat_observations,
)
from backend.app.data.eurostat_catalog import EUROSTAT_CATALOG
from backend.app.db.database import SessionLocal
from backend.app.models.indicator import Indicator, IndicatorValue


def sync_eurostat_catalog() -> dict:
    results: dict[str, dict] = {}

    with SessionLocal() as db:
        for entry in EUROSTAT_CATALOG:
            code = entry["code"]
            nuts_level = int(entry.get("nuts_level", 3))
            geo_level_param = f"nuts{nuts_level}"

            try:
                payload = fetch_dataset(
                    entry["dataset_code"],
                    geo_level=geo_level_param,
                    filters=entry.get("filters") or {},
                )
                observations = parse_jsonstat_observations(
                    payload,
                    nuts_level=nuts_level,
                )

                indicator = db.scalar(
                    select(Indicator).where(Indicator.code == code)
                )
                if indicator is None:
                    indicator = Indicator(
                        code=code,
                        label=entry["label"],
                        unit=entry.get("unit"),
                        source="eurostat",
                        geo_level=entry.get("geo_level", "county"),
                        dataset_code=entry["dataset_code"],
                        theme=entry.get("theme"),
                    )
                    db.add(indicator)
                    db.flush()
                else:
                    indicator.label = entry["label"]
                    indicator.unit = entry.get("unit")
                    indicator.theme = entry.get("theme")
                    indicator.dataset_code = entry["dataset_code"]
                    indicator.geo_level = entry.get("geo_level", "county")

                upserted = 0
                for obs in observations:
                    statement = (
                        insert(IndicatorValue)
                        .values(
                            indicator_id=indicator.id,
                            geo_code=obs["geo_code"],
                            time_period=obs["time_period"],
                            value=obs["value"],
                        )
                        .on_conflict_do_update(
                            constraint="uq_indicator_geo_time",
                            set_={"value": obs["value"]},
                        )
                    )
                    db.execute(statement)
                    upserted += 1

                db.commit()
                results[code] = {
                    "status": "ok",
                    "observations": upserted,
                }
            except Exception as exc:  # noqa: BLE001
                db.rollback()
                results[code] = {
                    "status": "error",
                    "error": str(exc),
                }

    return results
