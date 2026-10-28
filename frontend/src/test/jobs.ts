import type { Facets, Job, JobListResponse } from "../api/types";

export const pythonJob: Job = {
  id: "11111111-1111-1111-1111-111111111111",
  title: "Senior Python Engineer",
  company_name: "Northwind Labs",
  description: "Python FastAPI PostgreSQL",
  canonical_url: "https://example.com/jobs/python",
  apply_url: "https://example.com/jobs/python",
  location_text: "Remote, Brazil",
  country_code: "BR",
  workplace_type: "remote",
  employment_type: "full-time",
  seniority: "senior",
  salary_min: null,
  salary_max: null,
  salary_currency: null,
  technologies: ["Python"],
  role_category: "software-engineering",
  published_at: "2026-10-01T00:00:00Z",
  first_seen_at: "2026-10-01T00:00:00Z",
};

export const jobList: JobListResponse = {
  items: [pythonJob],
  pagination: { page: 1, page_size: 20, total: 1, pages: 1 },
};

export const facets: Facets = {
  technologies: { Python: 1 },
  countries: { BR: 1 },
  role_categories: { "software-engineering": 1 },
  workplace_types: { remote: 1 },
};
