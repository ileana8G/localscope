"""CLI helpers for data sync jobs."""

from __future__ import annotations

import argparse
import json

from backend.app.connectors.eea_aq import sync_aq_stations
from backend.app.services.eurostat_import import sync_eurostat_catalog
from backend.app.services.locality_import import import_localities


def main() -> None:
    parser = argparse.ArgumentParser(description="LocalScope data sync")
    parser.add_argument(
        "job",
        choices=["localities", "eurostat", "aq-stations", "all"],
    )
    args = parser.parse_args()

    results: dict = {}

    if args.job in {"localities", "all"}:
        results["localities"] = import_localities()
    if args.job in {"eurostat", "all"}:
        results["eurostat"] = sync_eurostat_catalog()
    if args.job in {"aq-stations", "all"}:
        results["aq_stations"] = sync_aq_stations()

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
