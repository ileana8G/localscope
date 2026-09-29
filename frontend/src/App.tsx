import { useState } from "react";
import { searchLocalities, type Locality } from "./services/api";

function App() {
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
            <strong>{locality.name}</strong> — {locality.county}
          </li>
        ))}
      </ul>
    </main>
  );
}

export default App;
