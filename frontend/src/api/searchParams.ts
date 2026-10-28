import type { SearchState } from "./types";

export const defaultSearch: SearchState = {
  q: "",
  technologies: [],
  country: "",
  workplace_type: "",
  role_category: "",
  seniority: "",
  sort: "relevance",
  page: 1,
};

export function parseSearchParams(params: URLSearchParams): SearchState {
  const technologies = params.getAll("technologies");
  const sort = params.get("sort") === "newest" ? "newest" : "relevance";
  const page = Number(params.get("page") || "1");
  return {
    q: params.get("q") ?? "",
    technologies,
    country: params.get("country") ?? "",
    workplace_type: params.get("workplace_type") ?? "",
    role_category: params.get("role_category") ?? "",
    seniority: params.get("seniority") ?? "",
    sort,
    page: Number.isFinite(page) && page > 0 ? page : 1,
  };
}

export function serializeSearchParams(state: SearchState): URLSearchParams {
  const params = new URLSearchParams();
  if (state.q) params.set("q", state.q);
  for (const technology of state.technologies) params.append("technologies", technology);
  if (state.country) params.set("country", state.country);
  if (state.workplace_type) params.set("workplace_type", state.workplace_type);
  if (state.role_category) params.set("role_category", state.role_category);
  if (state.seniority) params.set("seniority", state.seniority);
  if (state.sort !== "relevance") params.set("sort", state.sort);
  if (state.page > 1) params.set("page", String(state.page));
  return params;
}
