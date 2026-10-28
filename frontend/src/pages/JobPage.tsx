import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { getJob } from "../api/client";
import { JobDescription, JobFacts, JobSource } from "../components/JobDescription";

export function JobPage() {
  const { jobId = "" } = useParams();
  const query = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => getJob(jobId),
    enabled: Boolean(jobId),
  });

  if (query.isLoading) return <main className="page"><p className="status">Loading…</p></main>;
  if (query.isError || !query.data) {
    return (
      <main className="page">
        <p className="status error">This job is no longer listed.</p>
        <Link to="/">Back to search</Link>
      </main>
    );
  }

  const job = query.data;
  return (
    <main className="page detail">
      <Link to={`/${window.location.search}`}>Back to search</Link>
      <h1>{job.title}</h1>
      <p className="muted">
        {job.company_name}
        {job.location_text ? ` · ${job.location_text}` : ""}
      </p>
      <JobSource job={job} />
      <p className="tags">
        {job.technologies.map((technology) => (
          <span key={technology}>{technology}</span>
        ))}
      </p>
      <JobFacts job={job} />
      <a className="apply" href={job.apply_url} target="_blank" rel="noreferrer noopener">
        Apply on original site
      </a>
      <JobDescription job={job} />
    </main>
  );
}
