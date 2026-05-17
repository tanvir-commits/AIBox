import { useCallback, useEffect, useState } from "react";
import { apiFetch, apiUpload } from "../api/client";
import { useAuth } from "../auth/AuthContext";

type DocumentRow = {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  sha256: string;
  status: string;
  chunk_count: number;
  page_count: number | null;
  error_message: string | null;
  created_at: string;
};

function statusStyle(status: string) {
  switch (status) {
    case "indexed":
      return "bg-emerald-500/15 text-emerald-300 ring-emerald-500/30";
    case "failed":
      return "bg-red-500/15 text-red-300 ring-red-500/30";
    default:
      return "bg-amber-500/15 text-amber-200 ring-amber-500/30";
  }
}

export function DocumentsPage() {
  const { user } = useAuth();
  const [docs, setDocs] = useState<DocumentRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const rows = await apiFetch<DocumentRow[]>("/api/documents");
      setDocs(rows);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const canWrite = user?.role !== "read_only";

  async function onPickFile(file: File | null) {
    if (!file || !canWrite) return;
    setUploading(true);
    setError(null);
    try {
      await apiUpload<DocumentRow>("/api/documents/upload", file);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setUploading(false);
    }
  }

  async function onDelete(id: string) {
    if (!canWrite) return;
    if (!window.confirm("Delete this document and its vectors?")) return;
    setError(null);
    try {
      await apiFetch(`/api/documents/${id}`, { method: "DELETE" });
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold">Documents</h2>
          <p className="mt-1 max-w-2xl text-sm text-zinc-400">
            Upload PDF, DOCX, TXT, MD, or CSV (one file at a time). Each file is
            hashed, parsed, chunked, embedded, and indexed for chat citations.
          </p>
        </div>
        {canWrite ? (
          <label className="inline-flex cursor-pointer items-center gap-2 rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-60">
            <input
              type="file"
              accept=".pdf,.docx,.txt,.md,.csv"
              className="hidden"
              disabled={uploading}
              onChange={(e) => {
                const f = e.target.files?.[0] ?? null;
                e.target.value = "";
                void onPickFile(f);
              }}
            />
            {uploading ? "Uploading…" : "Upload file"}
          </label>
        ) : (
          <p className="text-sm text-zinc-500">Read-only accounts cannot upload.</p>
        )}
      </div>

      {error ? (
        <div className="rounded-md border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {error}
        </div>
      ) : null}

      <div className="overflow-hidden rounded-lg border border-zinc-800">
        <table className="min-w-full divide-y divide-zinc-800 text-sm">
          <thead className="bg-zinc-900/60 text-left text-xs uppercase tracking-wide text-zinc-500">
            <tr>
              <th className="px-4 py-3">File</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Size</th>
              <th className="px-4 py-3">Chunks</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800 bg-zinc-950/40">
            {loading ? (
              <tr>
                <td className="px-4 py-6 text-zinc-500" colSpan={6}>
                  Loading…
                </td>
              </tr>
            ) : docs.length === 0 ? (
              <tr>
                <td className="px-4 py-6 text-zinc-500" colSpan={6}>
                  No documents yet. Upload a file to index it.
                </td>
              </tr>
            ) : (
              docs.map((d) => (
                <tr key={d.id} className="hover:bg-zinc-900/40">
                  <td className="px-4 py-3 font-medium text-zinc-100">{d.filename}</td>
                  <td className="px-4 py-3 text-zinc-400">{d.file_type}</td>
                  <td className="px-4 py-3 text-zinc-400">{d.file_size.toLocaleString()} B</td>
                  <td className="px-4 py-3 text-zinc-400">{d.chunk_count}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex rounded-full px-2 py-0.5 text-xs ring-1 ring-inset ${statusStyle(
                        d.status,
                      )}`}
                    >
                      {d.status}
                    </span>
                    {d.error_message ? (
                      <div className="mt-1 max-w-md truncate text-xs text-red-300" title={d.error_message}>
                        {d.error_message}
                      </div>
                    ) : null}
                  </td>
                  <td className="px-4 py-3 text-right">
                    {canWrite ? (
                      <button
                        type="button"
                        className="text-xs text-red-300 hover:text-red-200"
                        onClick={() => void onDelete(d.id)}
                      >
                        Delete
                      </button>
                    ) : (
                      <span className="text-xs text-zinc-600">—</span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
