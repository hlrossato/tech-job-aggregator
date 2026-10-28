type Props = {
  value: string;
  onChange: (value: string) => void;
};

export function SearchBar({ value, onChange }: Props) {
  return (
    <label className="search-bar">
      <span className="sr-only">Search jobs</span>
      <input
        name="q"
        value={value}
        placeholder="Search titles or technologies, for example Python or C#"
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}
