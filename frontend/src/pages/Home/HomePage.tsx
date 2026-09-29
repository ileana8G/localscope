import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { searchLocalities, type Locality } from "../../services/api";

export default function HomePage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Locality[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  const handleSearch = useCallback(async (searchQuery: string) => {
    const trimmedQuery = searchQuery.trim();

    if (trimmedQuery.length < 2) {
      setResults([]);
      setError(null);
      return;
    }

    abortControllerRef.current?.abort();

    const controller = new AbortController();
    abortControllerRef.current = controller;

    setLoading(true);
    setError(null);

    try {
      const data = await searchLocalities(
        trimmedQuery,
        20,
        controller.signal,
      );

      setResults(data);
    } catch (error) {
      if (error instanceof DOMException && error.name === "AbortError") {
        return;
      }

      setError("Nu am putut încărca localitățile.");
    } finally {
      if (!controller.signal.aborted) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    const trimmedQuery = query.trim();

    if (trimmedQuery.length < 2) {
      setResults([]);
      setError(null);
      return;
    }

    const timeoutId = setTimeout(() => {
      handleSearch(trimmedQuery);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query, handleSearch]);

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
        />

        <button
          onClick={() => handleSearch(query)}
          disabled={loading}
        >
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