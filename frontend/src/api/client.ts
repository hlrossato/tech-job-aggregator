import type { Facets, Job, JobListResponse, SearchState } from "./types";
import { serializeSearchParams } from "./searchParams";

const API_BASE = import.meta.env.VITE_API_URL || "/api/v1";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function searchJobs(state: SearchState): Promise<JobListResponse> {
  const params = serializeSearchParams(state);
  const query = params.toString();
  return getJson(`/jobs${query ? `?${query}` : ""}`);
}

export function getJob(id: string): Promise<Job> {
  return getJson(`/jobs/${id}`);
}

export function getFacets(): Promise<Facets> {
  return getJson("/jobs/facets");
}
