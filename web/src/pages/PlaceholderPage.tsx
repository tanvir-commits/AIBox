export function PlaceholderPage({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="max-w-2xl space-y-3">
      <h2 className="text-xl font-semibold text-zinc-100">{title}</h2>
      <p className="text-sm leading-relaxed text-zinc-400">{description}</p>
      <div className="rounded-lg border border-dashed border-zinc-700 bg-zinc-900/30 p-6 text-sm text-zinc-500">
        UI scaffold — wiring and behavior land in later phases (upload, RAG,
        Ollama, watched folders, admin metrics).
      </div>
    </div>
  );
}
