import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, expect, test, vi } from "vitest";

import { facets, jobList, pythonJob } from "../test/jobs";
import { JobPage } from "./JobPage";
import { SearchPage } from "./SearchPage";

const searchJobs = vi.fn();
const getFacets = vi.fn();
const getJob = vi.fn();

vi.mock("../api/client", () => ({
  searchJobs: (...args: unknown[]) => searchJobs(...args),
  getFacets: (...args: unknown[]) => getFacets(...args),
  getJob: (...args: unknown[]) => getJob(...args),
}));

function renderApp(path = "/") {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[path]}>
        <Routes>
          <Route path="/" element={<SearchPage />} />
          <Route path="/jobs/:jobId" element={<JobPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  searchJobs.mockReset();
  getFacets.mockReset();
  getJob.mockReset();
  searchJobs.mockResolvedValue(jobList);
  getFacets.mockResolvedValue(facets);
  getJob.mockResolvedValue(pythonJob);
});

test("search filter detail and outbound apply", async () => {
  const user = userEvent.setup();
  renderApp();

  expect(await screen.findByText("Senior Python Engineer")).toBeInTheDocument();
  await screen.findByRole("option", { name: /Python/ });
  await user.type(
    screen.getByPlaceholderText(/Search titles or technologies/i),
    "python",
  );
  expect(searchJobs).toHaveBeenCalled();

  await user.selectOptions(screen.getByLabelText("Technology"), "Python");
  await user.click(screen.getByRole("link", { name: "Senior Python Engineer" }));
  expect(await screen.findByText("Apply on original site")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "Apply on original site" })).toHaveAttribute(
    "href",
    pythonJob.apply_url,
  );
  expect(screen.getByRole("heading", { name: "About the role" })).toBeInTheDocument();
  expect(screen.getByText("FastAPI")).toBeInTheDocument();
  expect(screen.getByText("Security")).toBeInTheDocument();
  expect(screen.getByText("Atlanta, South San Francisco HQ")).toBeInTheDocument();
  expect(screen.getByText("Remote in United States")).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "Hybrid work at Stripe" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "Pay and benefits" })).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "Greenhouse" })).toHaveAttribute(
    "href",
    "https://example.com/jobs",
  );
});

test("shows empty state", async () => {
  searchJobs.mockResolvedValue({
    items: [],
    pagination: { page: 1, page_size: 20, total: 0, pages: 0 },
  });
  renderApp();
  expect(await screen.findByText(/No jobs matched/i)).toBeInTheDocument();
});
