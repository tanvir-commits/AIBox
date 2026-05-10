import { useEffect, useState } from "react";
import { apiFetch } from "../api/client";

type StatusResponse = {
  app: string;
  healthy: boolean;
  providers: { llm: string; embedding: string };
  dependencies: {
    postgres: { ok: boolean; detail: string };
    qdrant: { ok: boolean; detail: string };
  };
};

export function SystemStatusPanel() {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const s = await apiFetch<StatusResponse>("/api/system/status");
        if (!cancelled) setStatus(s);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section className="max-w-3xl rounded-lg border border-zinc-800 bg-zinc-900/40 p-5">
      <h3 className="mb-3 text-sm font-medium uppercase tracking-wide text-zinc-500">
        System status
      </h3>
      {error ? (
        <p className="text-sm text-red-400">{error}</p>
      ) : !status ? (
        <p className="text-sm text-zinc-500">Loading…</p>
      ) : (
        <dl className="grid gap-3 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-zinc-500">Healthy</dt>
            <dd
              className={
                status.healthy ? "font-mono text-emerald-400" : "font-mono text-amber-400"
              }
            >
              {String(status.healthy)}
            </dd>
          </div>
          <div>
            <dt className="text-zinc-500">App</dt>
            <dd className="font-mono text-zinc-200">{status.app}</dd>
          </div>
          <div className="sm:col-span-2">
            <dt className="text-zinc-500">PostgreSQL</dt>
            <dd className="font-mono text-xs text-zinc-300">
              {status.dependencies.postgres.ok ? "ok" : "fail"} —{" "}
              {status.dependencies.postgres.detail}
            </dd>
          </div>
          <div className="sm:col-span-2">
            <dt className="text-zinc-500">Qdrant</dt>
            <dd className="font-mono text-xs text-zinc-300">
              {status.dependencies.qdrant.ok ? "ok" : "fail"} —{" "}
              {status.dependencies.qdrant.detail}
            </dd>
          </div>
          <div>
            <dt className="text-zinc-500">LLM</dt>
            <dd className="font-mono">{status.providers.llm}</dd>
          </div>
          <div>
            <dt className="text-zinc-500">Embeddings</dt>
            <dd className="font-mono">{status.providers.embedding}</dd>
          </div>
        </dl>
      )}
    </section>
  );
}
