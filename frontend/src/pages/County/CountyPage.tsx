import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import PlaceSections from "../../components/Place/PlaceSections";
import {
  getCountyDashboard,
  type PlaceDashboard,
} from "../../services/api";

export default function CountyPage() {
  const { nuts3 } = useParams();
  const [dashboard, setDashboard] = useState<PlaceDashboard | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!nuts3) return;

    getCountyDashboard(nuts3)
      .then(setDashboard)
      .catch(() => setError("Nu am putut încărca județul."));
  }, [nuts3]);

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

  return (
    <main>
      <Link to="/">← Înapoi la căutare</Link>

      <header>
        <h1>{String(place.name)}</h1>
        <p>
          {String(place.nuts3)} · NUTS2 {String(place.nuts2)}
        </p>
      </header>

      <PlaceSections
        dashboard={dashboard}
        general={
          <section>
            <h2>Date generale</h2>
            <dl>
              <dt>Cod NUTS3</dt>
              <dd>{String(place.nuts3)}</dd>
              <dt>Cod NUTS2</dt>
              <dd>{String(place.nuts2)}</dd>
            </dl>
          </section>
        }
      />
    </main>
  );
}
