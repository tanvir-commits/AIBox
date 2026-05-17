import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "../api/client";

type OllamaModelRow = {
  name: string;
  size: number | null;
  modified_at: string | null;
};

type OllamaModelsResponse = {
  ollama_base_url: string;
  configured_model: string;
  default_llm_provider: string;
  reachable: boolean;
  detail: string | null;
  models: OllamaModelRow[];
};

function formatBytes(n: number | null): string {
  if (n == null || !Number.isFinite(n)) return "—";
  const units = ["B", "KB", "MB", "GB", "TB"];
  let v = n;
  let i = 0;
  while (v >= 1024 && i < units.length - 1) {
    v /= 1024;
    i += 1;
  }
  const digits = i === 0 ? 0 : v >= 10 ? 0 : 1;
  return `${v.toFixed(digits)} ${units[i]}`;
}

export function ModelsPage() {
  const [data, setData] = useState<OllamaModelsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const row = await apiFetch<OllamaModelsResponse>("/api/models/ollama");
      setData(row);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const configured = data?.configured_model?.trim() ?? "";

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold">Models</h2>
          <p className="mt-1 max-w-2xl text-sm text-zinc-400">
            Installed models from your Ollama server (<code className="text-zinc-300">/api/tags</code>
            ). The chat default is <code className="text-zinc-300">OLLAMA_MODEL</code> in server
            config; restart the API after changing it.
          </p>
        </div>
        <button
          type="button"
          onClick={() => void load()}
          disabled={loading}
          className="rounded-md border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-200 hover:bg-zinc-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Refresh
        </button>
      </div>

      {error ? (
        <p className="text-sm text-red-400">{error}</p>
      ) : loading || !data ? (
        <p className="text-sm text-zinc-500">Loading…</p>
      ) : (
        <>
          <section className="max-w-3xl rounded-lg border border-zinc-800 bg-zinc-900/40 p-5">
            <h3 className="mb-3 text-sm font-medium uppercase tracking-wide text-zinc-500">
              Ollama
            </h3>
            <dl className="grid gap-3 text-sm sm:grid-cols-2">
              <div className="sm:col-span-2">
                <dt className="text-zinc-500">Base URL</dt>
                <dd className="font-mono text-xs text-zinc-300">{data.ollama_base_url}</dd>
              </div>
              <div>
                <dt className="text-zinc-500">LLM provider</dt>
                <dd className="font-mono text-zinc-200">{data.default_llm_provider}</dd>
              </div>
              <div>
                <dt className="text-zinc-500">Configured default model</dt>
                <dd className="font-mono text-zinc-200">{data.configured_model || "—"}</dd>
              </div>
              <div>
                <dt className="text-zinc-500">Reachable</dt>
                <dd
                  className={
                    data.reachable ? "font-mono text-emerald-400" : "font-mono text-amber-400"
                  }
                >
                  {String(data.reachable)}
                </dd>
              </div>
              {data.detail ? (
                <div className="sm:col-span-2">
                  <dt className="text-zinc-500">Detail</dt>
                  <dd className="font-mono text-xs text-zinc-300">{data.detail}</dd>
                </div>
              ) : null}
            </dl>
          </section>

          {data.reachable && data.models.length === 0 ? (
            <p className="text-sm text-zinc-500">Ollama returned no installed models.</p>
          ) : null}

          {data.models.length > 0 ? (
            <div className="overflow-x-auto rounded-lg border border-zinc-800">
              <table className="min-w-full divide-y divide-zinc-800 text-sm">
                <thead className="bg-zinc-900/60">
                  <tr>
                    <th className="px-4 py-2 text-left font-medium text-zinc-400">Name</th>
                    <th className="px-4 py-2 text-left font-medium text-zinc-400">Size</th>
                    <th className="px-4 py-2 text-left font-medium text-zinc-400">Modified</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800">
                  {data.models.map((m) => {
                    const isDefault =
                      configured.length > 0 &&
                      (m.name === configured || m.name.startsWith(`${configured}:`));
                    return (
                      <tr key={m.name} className="bg-zinc-950/40">
                        <td className="px-4 py-2 font-mono text-xs text-zinc-200">
                          <span className="align-middle">{m.name}</span>
                          {isDefault ? (
                            <span className="ml-2 inline-block rounded bg-emerald-500/15 px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide text-emerald-300 ring-1 ring-emerald-500/30">
                              default
                            </span>
                          ) : null}
                        </td>
                        <td className="px-4 py-2 font-mono text-xs text-zinc-400">
                          {formatBytes(m.size)}
                        </td>
                        <td className="px-4 py-2 font-mono text-xs text-zinc-500">
                          {m.modified_at ?? "—"}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : null}
        </>
      )}
    </div>
  );
}
