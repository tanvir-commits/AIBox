import { useId, useState } from "react";
import type { Citation } from "../types/chat";

type ChatSourcesProps = {
  citations: Citation[];
};

export function ChatSources({ citations }: ChatSourcesProps) {
  const panelId = useId();
  if (!citations.length) return null;

  return (
    <details className="group mt-3 rounded-lg border border-zinc-700/80 bg-zinc-900/40">
      <summary className="cursor-pointer list-none px-3 py-2 text-xs font-medium text-zinc-400 transition hover:bg-zinc-800/50 hover:text-zinc-200 [&::-webkit-details-marker]:hidden">
        <span className="inline-flex items-center gap-2">
          <span className="text-zinc-500 transition-transform group-open:rotate-90">▸</span>
          <span>Sources</span>
          <span className="rounded-full bg-zinc-800 px-2 py-0.5 font-mono text-[10px] text-emerald-400/90">
            {citations.length}
          </span>
          <span className="font-normal text-zinc-600 group-open:hidden">
            — tap to expand excerpts
          </span>
        </span>
      </summary>
      <div id={panelId} className="border-t border-zinc-800 px-2 py-2">
        <ol className="space-y-2">
          {citations.map((c, i) => (
            <CitationRow key={c.chunk_id} index={i + 1} citation={c} />
          ))}
        </ol>
      </div>
    </details>
  );
}

function CitationRow({ index, citation: c }: { index: number; citation: Citation }) {
  const [expanded, setExpanded] = useState(false);
  const excerpt = (c.excerpt ?? "").trim();
  const isLong = excerpt.length > 240;

  return (
    <li className="rounded-md border border-zinc-800/90 bg-zinc-950/50 px-3 py-2">
      <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
        <span className="inline-flex h-5 min-w-[1.25rem] items-center justify-center rounded bg-emerald-500/15 px-1 font-mono text-[11px] font-semibold text-emerald-400">
          {index}
        </span>
        <span className="break-all font-mono text-[11px] text-emerald-300">{c.filename}</span>
        {c.page_number != null ? (
          <span className="text-[11px] text-zinc-500">· p.{c.page_number}</span>
        ) : null}
      </div>
      {excerpt ? (
        <div className="mt-1.5">
          <p
            className={`text-[11px] leading-relaxed text-zinc-400 ${
              !expanded && isLong ? "line-clamp-4" : ""
            }`}
          >
            {excerpt}
          </p>
          {isLong ? (
            <button
              type="button"
              className="mt-1 text-[10px] font-medium text-emerald-500/90 hover:text-emerald-400"
              onClick={() => setExpanded((e) => !e)}
            >
              {expanded ? "Show less" : "Show full excerpt"}
            </button>
          ) : null}
        </div>
      ) : null}
    </li>
  );
}
