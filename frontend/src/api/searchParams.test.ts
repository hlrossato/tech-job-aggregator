import { expect, test } from "vitest";

import { parseSearchParams, serializeSearchParams } from "./searchParams";

test("round-trips search state in the URL", () => {
  const params = serializeSearchParams({
    q: "python",
    technologies: ["Python"],
    country: "BR",
    workplace_type: "remote",
    role_category: "software-engineering",
    seniority: "senior",
    sort: "newest",
    page: 2,
  });
  expect(params.toString()).toContain("q=python");
  const parsed = parseSearchParams(params);
  expect(parsed.q).toBe("python");
  expect(parsed.technologies).toEqual(["Python"]);
  expect(parsed.page).toBe(2);
  expect(parsed.sort).toBe("newest");
});
