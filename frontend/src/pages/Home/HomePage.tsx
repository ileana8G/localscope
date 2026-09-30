import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  searchCounties,
  searchLocalities,
  type County,
  type Locality,
} from "../../services/api";

type SearchMode = "localities" | "counties";

export default function HomePage() {
  const [mode, setMode] = useState<SearchMode>("localities");
  const [query, setQuery] = useState("");
  const [localities, setLocalities] = useState<Locality[]>([]);
  const [counties, setCounties] = useState<County[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  const handleSearch = useCallback(
    async (searchQuery: string, searchMode: SearchMode) => {
      const trimmedQuery = searchQuery.trim();

      if (trimmedQuery.length < 2) {
        setLocalities([]);
        setCounties([]);
        setError(null);
        return;
      }

      abortControllerRef.current?.abort();

      const controller = new AbortController();
      abortControllerRef.current = controller;

      setLoading(true);
      setError(null);

      try {
        if (searchMode === "localities") {
          const data = await searchLocalities(
            trimmedQuery,
            20,
            controller.signal,
          );
          setLocalities(data);
          setCounties([]);
        } else {
          const data = await searchCounties(
            trimmedQuery,
            20,
            controller.signal,
          );
          setCounties(data);
          setLocalities([]);
        }
      } catch (searchError) {
        if (
          searchError instanceof DOMException &&
          searchError.name === "AbortError"
        ) {
          return;
        }

        setError("Nu am putut încărca rezultatele.");
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    },
    [],
  );

  useEffect(() => {
    const trimmedQuery = query.trim();

    if (trimmedQuery.length < 2) {
      setLocalities([]);
      setCounties([]);
      setError(null);
      return;
    }

    const timeoutId = setTimeout(() => {
      handleSearch(trimmedQuery, mode);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query, mode, handleSearch]);

  return (
    <main>
      <h1>LocalScope</h1>
      <p>Descoperă ce se întâmplă în localitatea ta.</p>

      <div>
        <button
          type="button"
          onClick={() => setMode("localities")}
          aria-pressed={mode === "localities"}
        >
          Localități
        </button>
        <button
          type="button"
          onClick={() => setMode("counties")}
          aria-pressed={mode === "counties"}
        >
          Județe
        </button>
      </div>

      <div>
        <input
          type="search"
          value={query}
          placeholder={
            mode === "localities"
              ? "Caută o localitate..."
              : "Caută un județ..."
          }
          onChange={(event) => setQuery(event.target.value)}
        />

        <button
          onClick={() => handleSearch(query, mode)}
          disabled={loading}
        >
          {loading ? "Caut..." : "Caută"}
        </button>
      </div>

      {error && <p>{error}</p>}

      <ul>
        {mode === "localities" &&
          localities.map((locality) => (
            <li key={locality.siruta}>
              <Link to={`/locality/${locality.siruta}`}>
                <strong>{locality.name}</strong> — {locality.county}
              </Link>
            </li>
          ))}

        {mode === "counties" &&
          counties.map((county) => (
            <li key={county.nuts3}>
              <Link to={`/county/${county.nuts3}`}>
                <strong>{county.name}</strong> — {county.nuts3}
              </Link>
            </li>
          ))}
      </ul>
    </main>
  );
}
