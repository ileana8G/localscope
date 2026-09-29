import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getLocality, type Locality } from "../../services/api";
import LocalityHeader from "../../components/Locality/LocalityHeader";

export default function LocalityPage() {
  const { siruta } = useParams();
  const [locality, setLocality] = useState<Locality | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!siruta) return;

    getLocality(Number(siruta))
      .then(setLocality)
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

  if (!locality) {
    return (
      <main>
        <p>Se încarcă...</p>
      </main>
    );
  }

  return (
    <main>
      <Link to="/">← Înapoi la căutare</Link>

      <LocalityHeader locality={locality} />

      <section>
        <h2>Date generale</h2>

        <dl>
          <dt>SIRUTA</dt>
          <dd>{locality.siruta}</dd>

          <dt>Tip localitate</dt>
          <dd>{locality.locality_type ?? "—"}</dd>

          <dt>Populație</dt>
          <dd>{locality.population?.toLocaleString("ro-RO") ?? "—"}</dd>
        </dl>
      </section>
    </main>
  );
}
