import type { Job } from "../api/types";

export function JobSource({ job }: { job: Job }) {
  if (!job.source_name) return null;
  const label = job.source_name;
  return (
    <p className="source">
      From{" "}
      {job.source_url ? (
        <a href={job.source_url} target="_blank" rel="noreferrer noopener">
          {label}
        </a>
      ) : (
        label
      )}
    </p>
  );
}

export function JobFacts({ job }: { job: Job }) {
  const rows = [
    ["Company", job.company_name],
    ["Team", job.team],
    ["Office locations", job.office_locations],
    ["Remote location", job.remote_location],
    ["Employment type", job.employment_type],
  ].filter((row): row is [string, string] => Boolean(row[1]));
  if (rows.length === 0) return null;
  return (
    <dl className="facts">
      {rows.map(([label, value]) => (
        <div key={label}>
          <dt>{label}</dt>
          <dd>{value}</dd>
        </div>
      ))}
    </dl>
  );
}

export function JobDescription({ job }: { job: Job }) {
  if (job.description_html) {
    return (
      <article
        className="description"
        dangerouslySetInnerHTML={{ __html: job.description_html }}
      />
    );
  }
  return <article className="description plain">{job.description}</article>;
}
