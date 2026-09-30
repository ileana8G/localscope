const API_URL = import.meta.env.VITE_API_URL;

export type Locality = {
  id: number;
  siruta: number;
  name: string;
  county: string;
  county_id: number | null;
  siruta_sup: number | null;
  locality_type: string | null;
  population: number | null;
  latitude: number | null;
  longitude: number | null;
};

export type County = {
  id: number;
  name: string;
  nuts3: string;
  nuts2: string;
  latitude: number | null;
  longitude: number | null;
};

export type IndicatorSeries = {
  code: string;
  label: string;
  unit: string | null;
  source: string;
  geo_level: string;
  theme: string | null;
  values: { time_period: string; value: number | null }[];
};

export type PlaceDashboard = {
  place: Record<string, unknown>;
  stats: IndicatorSeries[];
  weather: {
    source?: string;
    forecast?: {
      current?: Record<string, number | string | null>;
      daily?: Record<string, Array<number | string | null>>;
    };
    climate?: {
      source: string;
      monthly: {
        month: string;
        avg_temperature_c: number | null;
        total_precipitation_mm: number | null;
      }[];
    };
    error?: string;
  } | null;
  air_quality: {
    source: string;
    station: {
      eoi_code: string;
      name: string;
      distance_km?: number;
      pollutants?: string | null;
    } | null;
    stations: {
      eoi_code: string;
      name: string;
      pollutants?: string | null;
    }[];
    note?: string;
  };
};

async function fetchJson<T>(url: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(url, { signal });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json();
}

export async function searchLocalities(
  query: string,
  limit = 20,
  signal?: AbortSignal,
): Promise<Locality[]> {
  return fetchJson(
    `${API_URL}/api/v1/localities/search?q=${encodeURIComponent(query)}&limit=${limit}`,
    signal,
  );
}

export async function getLocality(siruta: number): Promise<Locality> {
  return fetchJson(`${API_URL}/api/v1/localities/${siruta}`);
}

export async function getLocalityDashboard(
  siruta: number,
): Promise<PlaceDashboard> {
  return fetchJson(`${API_URL}/api/v1/localities/${siruta}/dashboard`);
}

export async function searchCounties(
  query: string,
  limit = 20,
  signal?: AbortSignal,
): Promise<County[]> {
  return fetchJson(
    `${API_URL}/api/v1/counties/search?q=${encodeURIComponent(query)}&limit=${limit}`,
    signal,
  );
}

export async function getCountyDashboard(
  nuts3: string,
): Promise<PlaceDashboard> {
  return fetchJson(`${API_URL}/api/v1/counties/${nuts3}/dashboard`);
}
