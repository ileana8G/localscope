import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import PlaceSections from "../../components/Place/PlaceSections";
import LocalityHeader from "../../components/Locality/LocalityHeader";
import {
  getLocalityDashboard,
  type PlaceDashboard,
} from "../../services/api";

export default function LocalityPage() {
  const { siruta } = useParams();
  const [dashboard, setDashboard] = useState<PlaceDashboard | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!siruta) return;

    getLocalityDashboard(Number(siruta))
      .then(setDashboard)
      .catch(() => setError("Nu am putut încărca localitatea."));
  }, [siruta]);

  if (error) {
    return (
      <main>
        <Link to="/">← Înapoi la căutare</Link>
        <p>{error}</p>
      </main>
    );
  }

  if (!dashboard) {
    return (
      <main>
        <p>Se încarcă...</p>
      </main>
    );
  }

  const place = dashboard.place;
  const locality = {
    id: Number(place.id),
    siruta: Number(place.siruta),
    name: String(place.name),
    county: String(place.county),
    county_id: null,
    siruta_sup: null,
    locality_type: (place.locality_type as string | null) ?? null,
    population: (place.population as number | null) ?? null,
    latitude: (place.latitude as number | null) ?? null,
    longitude: (place.longitude as number | null) ?? null,
  };

  return (
    <main>
      <Link to="/">← Înapoi la căutare</Link>

      <LocalityHeader locality={locality} />

      {place.county_nuts3 ? (
        <p>
          <Link to={`/county/${place.county_nuts3}`}>
            Vezi județul {String(place.county)}
          </Link>
        </p>
      ) : null}

      <PlaceSections
        dashboard={dashboard}
        general={
          <section>
            <h2>Date generale</h2>
            <dl>
              <dt>SIRUTA</dt>
              <dd>{locality.siruta}</dd>
              <dt>Tip localitate</dt>
              <dd>{locality.locality_type ?? "—"}</dd>
              <dt>Populație</dt>
              <dd>
                {locality.population?.toLocaleString("ro-RO") ?? "—"}
              </dd>
            </dl>
          </section>
        }
      />
    </main>
  );
}
