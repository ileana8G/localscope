import type { Locality } from "../../services/api";

type LocalityHeaderProps = {
  locality: Locality;
};

export default function LocalityHeader({
  locality,
}: LocalityHeaderProps) {
  return (
    <header>
      <h1>{locality.name}</h1>
      <p>{locality.county}</p>
    </header>
  );
}
