export type WorkplaceType = "remote" | "hybrid" | "onsite" | "unspecified";

export type Job = {
  id: string;
  title: string;
  company_name: string;
  description: string;
  canonical_url: string;
  apply_url: string;
  location_text: string | null;
  country_code: string | null;
  workplace_type: WorkplaceType;
  employment_type: string | null;
  seniority: string | null;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string | null;
  technologies: string[];
  role_category: string | null;
  published_at: string | null;
  first_seen_at: string;
  description_html: string | null;
  source_name: string | null;
  source_url: string | null;
  team: string | null;
  office_locations: string | null;
  remote_location: string | null;
};

export type JobListResponse = {
  items: Job[];
  pagination: {
    page: number;
    page_size: number;
    total: number;
    pages: number;
  };
};

export type Facets = {
  technologies: Record<string, number>;
  countries: Record<string, number>;
  role_categories: Record<string, number>;
  workplace_types: Record<string, number>;
};

export type SearchState = {
  q: string;
  technologies: string[];
  country: string;
  workplace_type: string;
  role_category: string;
  seniority: string;
  sort: "relevance" | "newest";
  page: number;
};
