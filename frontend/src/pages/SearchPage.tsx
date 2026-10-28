import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import { useSearchParams } from "react-router-dom";

import { getFacets, searchJobs } from "../api/client";
import { defaultSearch, parseSearchParams, serializeSearchParams } from "../api/searchParams";
import type { SearchState } from "../api/types";
import { Filters } from "../components/Filters";
import { JobCard } from "../components/JobCard";
import { Pagination } from "../components/Pagination";
import { SearchBar } from "../components/SearchBar";

export function SearchPage() {
  const [params, setParams] = useSearchParams();
  const state = useMemo(() => parseSearchParams(params), [params]);

  function update(patch: Partial<SearchState>) {
    const next = { ...defaultSearch, ...state, ...patch };
    if (!("page" in patch)) next.page = 1;
    setParams(serializeSearchParams(next), { replace: true });
  }

  const jobsQuery = useQuery({
    queryKey: ["jobs", state],
    queryFn: () => searchJobs(state),
  });
  const facetsQuery = useQuery({
    queryKey: ["facets"],
    queryFn: getFacets,
  });

  return (
    <main className="page">
      <header className="hero">
        <p className="eyebrow">Public technology roles</p>
        <h1>Tech Jobs</h1>
        <p className="lede">
          Search open software, cloud, data and DevOps jobs. Apply on the original posting.
        </p>
        <SearchBar value={state.q} onChange={(q) => update({ q })} />
        <Filters state={state} facets={facetsQuery.data} onChange={update} />
      </header>

      {jobsQuery.isLoading && <p className="status">Searching…</p>}
      {jobsQuery.isError && <p className="status error">Could not load jobs.</p>}
      {jobsQuery.data?.pagination.total === 0 && (
        <p className="status">No jobs matched those filters.</p>
      )}

      <section className="results" aria-live="polite">
        {jobsQuery.data?.items.map((job) => (
          <JobCard key={job.id} job={job} />
        ))}
      </section>

      {jobsQuery.data && (
        <Pagination
          page={jobsQuery.data.pagination.page}
          pages={jobsQuery.data.pagination.pages}
          onPage={(page) => update({ page })}
        />
      )}
    </main>
  );
}
