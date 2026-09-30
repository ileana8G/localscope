import type { ReactNode } from "react";
import type { IndicatorSeries, PlaceDashboard } from "../../services/api";

type PlaceSectionsProps = {
  dashboard: PlaceDashboard;
  general?: ReactNode;
};

function latestValue(series: IndicatorSeries): string {
  const last = series.values[series.values.length - 1];
  if (!last || last.value == null) return "—";
  return `${last.value.toLocaleString("ro-RO")}${series.unit ? ` ${series.unit}` : ""} (${last.time_period})`;
}

export default function PlaceSections({
  dashboard,
  general,
}: PlaceSectionsProps) {
  const current = dashboard.weather?.forecast?.current;
  const climate = dashboard.weather?.climate?.monthly ?? [];
  const aq = dashboard.air_quality;

  return (
    <>
      {general}

      <section>
        <h2>Statistici (Eurostat)</h2>
        {dashboard.stats.length === 0 ? (
          <p>Nu există indicatori sincronizați pentru acest nivel.</p>
        ) : (
          <dl>
            {dashboard.stats.map((series) => (
              <div key={series.code}>
                <dt>
                  {series.label}
                  {series.geo_level === "county" ? " — județ" : ""}
                </dt>
                <dd>{latestValue(series)}</dd>
              </div>
            ))}
          </dl>
        )}
      </section>

      <section>
        <h2>Meteo și climat</h2>
        {dashboard.weather?.error && <p>{dashboard.weather.error}</p>}
        {!dashboard.weather && <p>Coordonate indisponibile.</p>}
        {current && (
          <dl>
            <dt>Temperatură actuală</dt>
            <dd>{String(current.temperature_2m ?? "—")} °C</dd>
            <dt>Umiditate</dt>
            <dd>{String(current.relative_humidity_2m ?? "—")} %</dd>
            <dt>Vânt</dt>
            <dd>{String(current.wind_speed_10m ?? "—")} km/h</dd>
          </dl>
        )}
        {climate.length > 0 && (
          <>
            <h3>Climat ERA5 (ultimele luni)</h3>
            <ul>
              {climate.slice(-6).map((row) => (
                <li key={row.month}>
                  {row.month}: {row.avg_temperature_c ?? "—"} °C,{" "}
                  {row.total_precipitation_mm ?? "—"} mm
                </li>
              ))}
            </ul>
          </>
        )}
      </section>

      <section>
        <h2>Calitate aer (EEA)</h2>
        {aq.note && <p>{aq.note}</p>}
        {aq.station && (
          <dl>
            <dt>Stație apropiată</dt>
            <dd>
              {aq.station.name} ({aq.station.eoi_code})
              {aq.station.distance_km != null
                ? ` — ${aq.station.distance_km} km`
                : ""}
            </dd>
            <dt>Poluanți raportați</dt>
            <dd>{aq.station.pollutants ?? "—"}</dd>
          </dl>
        )}
        {!aq.station && aq.stations.length > 0 && (
          <ul>
            {aq.stations.slice(0, 10).map((station) => (
              <li key={station.eoi_code}>
                {station.name} ({station.eoi_code})
                {station.pollutants ? ` — ${station.pollutants}` : ""}
              </li>
            ))}
          </ul>
        )}
      </section>
    </>
  );
}
