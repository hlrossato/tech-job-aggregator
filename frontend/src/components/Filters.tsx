import type { Facets, SearchState } from "../api/types";

type Props = {
  state: SearchState;
  facets: Facets | undefined;
  onChange: (patch: Partial<SearchState>) => void;
};

function options(record: Record<string, number> | undefined) {
  return Object.entries(record ?? {}).sort((left, right) => right[1] - left[1]);
}

export function Filters({ state, facets, onChange }: Props) {
  return (
    <div className="filters">
      <select
        aria-label="Technology"
        value={state.technologies[0] ?? ""}
        onChange={(event) =>
          onChange({ technologies: event.target.value ? [event.target.value] : [] })
        }
      >
        <option value="">All technologies</option>
        {options(facets?.technologies).map(([name, count]) => (
          <option key={name} value={name}>
            {name} ({count})
          </option>
        ))}
      </select>
      <select
        aria-label="Country"
        value={state.country}
        onChange={(event) => onChange({ country: event.target.value })}
      >
        <option value="">All countries</option>
        {options(facets?.countries).map(([name, count]) => (
          <option key={name} value={name}>
            {name} ({count})
          </option>
        ))}
      </select>
      <select
        aria-label="Workplace"
        value={state.workplace_type}
        onChange={(event) => onChange({ workplace_type: event.target.value })}
      >
        <option value="">Any workplace</option>
        <option value="remote">Remote</option>
        <option value="hybrid">Hybrid</option>
        <option value="onsite">On-site</option>
      </select>
      <select
        aria-label="Role"
        value={state.role_category}
        onChange={(event) => onChange({ role_category: event.target.value })}
      >
        <option value="">All roles</option>
        {options(facets?.role_categories).map(([name, count]) => (
          <option key={name} value={name}>
            {name} ({count})
          </option>
        ))}
      </select>
      <select
        aria-label="Sort"
        value={state.sort}
        onChange={(event) =>
          onChange({ sort: event.target.value as SearchState["sort"] })
        }
      >
        <option value="relevance">Relevance</option>
        <option value="newest">Newest</option>
      </select>
    </div>
  );
}
