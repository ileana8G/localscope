import { useEffect, useState } from "react";
import { Link, Route, Routes, useParams } from "react-router-dom";
import {
  getLocality,
  searchLocalities,
  type Locality,
} from "./services/api";

function HomePage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Locality[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSearch() {
    const trimmedQuery = query.trim();

    if (trimmedQuery.length < 2) {
      setResults([]);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await searchLocalities(trimmedQuery);
      setResults(data);
    } catch {
      setError("Nu am putut încărca localitățile.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>LocalScope</h1>
      <p>Descoperă ce se întâmplă în localitatea ta.</p>

      <div>
        <input
          type="search"
          value={query}
          placeholder="Caută o localitate..."
          onChange={(event) => setQuery(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              handleSearch();
            }
          }}
        />

        <button onClick={handleSearch} disabled={loading}>
          {loading ? "Caut..." : "Caută"}
        </button>
      </div>

      {error && <p>{error}</p>}

      <ul>
        {results.map((locality) => (
          <li key={locality.siruta}>
            <Link to={`/locality/${locality.siruta}`}>
              <strong>{locality.name}</strong> — {locality.county}
            </Link>
          </li>
        ))}
      </ul>
    </main>
  );
}

function LocalityPage() {
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

      <h1>{locality.name}</h1>
      <p>{locality.county}</p>

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
    </main>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/locality/:siruta" element={<LocalityPage />} />
    </Routes>
  );
}

export default App;
