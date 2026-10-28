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
  employment_type: "Full time",
  seniority: "senior",
  salary_min: null,
  salary_max: null,
  salary_currency: null,
  technologies: ["Python"],
  role_category: "software-engineering",
  published_at: "2026-10-01T00:00:00Z",
  first_seen_at: "2026-10-01T00:00:00Z",
  description_html:
    "<h2>About the role</h2><ul><li>Python</li><li>FastAPI</li></ul><h2>Hybrid work at Stripe</h2><p>Office or remote.</p><h2>Pay and benefits</h2><p>Annual base salary range.</p>",
  source_name: "Greenhouse",
  source_url: "https://example.com/jobs",
  team: "Security",
  office_locations: "Atlanta, South San Francisco HQ",
  remote_location: "Remote in United States",
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
