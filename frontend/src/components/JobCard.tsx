import { Link } from "react-router-dom";

import type { Job } from "../api/types";

function formatDate(value: string | null) {
  if (!value) return "Date unknown";
  return new Date(value).toLocaleDateString();
}

export function JobCard({ job }: { job: Job }) {
  return (
    <article className="job-card">
      <div>
        <Link to={`/jobs/${job.id}${window.location.search}`} className="job-title">
          {job.title}
        </Link>
        <p className="muted">
          {job.company_name}
          {job.location_text ? ` · ${job.location_text}` : ""}
          {` · ${formatDate(job.published_at)}`}
        </p>
        <p className="tags">
          {job.technologies.slice(0, 5).map((technology) => (
            <span key={technology}>{technology}</span>
          ))}
        </p>
      </div>
      <a className="apply" href={job.apply_url} target="_blank" rel="noreferrer noopener">
        Apply
      </a>
    </article>
  );
}
