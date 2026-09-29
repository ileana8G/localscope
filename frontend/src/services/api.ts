const API_URL = import.meta.env.VITE_API_URL;

export type Locality = {
  id: number;
  siruta: number;
  name: string;
  county: string;
  siruta_sup: number | null;
  locality_type: string | null;
  population: number | null;
};

export async function searchLocalities(
  query: string,
  limit = 20,
): Promise<Locality[]> {
  const response = await fetch(
    `${API_URL}/api/v1/localities/search?q=${encodeURIComponent(query)}&limit=${limit}`,
  );

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json();
}
