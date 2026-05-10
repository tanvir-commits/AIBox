import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { ChatSources } from "../components/ChatSources";
import { apiFetch } from "../api/client";
import type { Citation } from "../types/chat";
import { formatAssistantReplyForDisplay } from "../utils/chatDisplay";

type ChatTurn = {
  session_id: string;
  reply: string;
  citations: Citation[];
};

type ChatMessage = {
  id: string;
  role: string;
  content: string;
  citations: Citation[] | null;
  created_at: string;
};

type SessionRow = { id: string; title: string; updated_at: string | null };

export function ChatPage() {
  const [sessions, setSessions] = useState<SessionRow[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSessions = useCallback(async () => {
    setError(null);
    try {
      const rows = await apiFetch<SessionRow[]>("/api/chat/sessions");
      setSessions(rows);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, []);

  const loadSession = useCallback(async (id: string) => {
    setError(null);
    try {
      const detail = await apiFetch<{
        id: string;
        messages: ChatMessage[];
      }>(`/api/chat/sessions/${id}`);
      setMessages(detail.messages);
      setActiveSessionId(detail.id);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, []);

  useEffect(() => {
    void loadSessions();
  }, [loadSessions]);

  const title = useMemo(
    () => (activeSessionId ? "Continue chat" : "New chat"),
    [activeSessionId],
  );

  async function submitChat() {
    const text = input.trim();
    if (!text || busy) return;
    setBusy(true);
    setError(null);
    try {
      const res = await apiFetch<ChatTurn>("/api/chat", {
        method: "POST",
        body: JSON.stringify({
          session_id: activeSessionId,
          message: text,
        }),
      });
      setInput("");
      setActiveSessionId(res.session_id);
      await loadSession(res.session_id);
      await loadSessions();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  function onSend(e: FormEvent) {
    e.preventDefault();
    void submitChat();
  }

  async function onNewChat() {
    setActiveSessionId(null);
    setMessages([]);
    setInput("");
    setError(null);
  }

  async function onDeleteSession(id: string) {
    if (!window.confirm("Delete this conversation?")) return;
    setError(null);
    try {
      await apiFetch(`/api/chat/sessions/${id}`, { method: "DELETE" });
      if (activeSessionId === id) {
        await onNewChat();
      }
      await loadSessions();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  return (
    <div className="flex min-h-[calc(100vh-8rem)] flex-col gap-4 lg:flex-row">
      <aside className="w-full shrink-0 rounded-lg border border-zinc-800 bg-zinc-900/40 lg:w-64">
        <div className="flex items-center justify-between border-b border-zinc-800 px-3 py-2">
          <span className="text-xs font-medium uppercase tracking-wide text-zinc-500">
            Chats
          </span>
          <button
            type="button"
            className="text-xs text-emerald-400 hover:text-emerald-300"
            onClick={() => void onNewChat()}
          >
            New
          </button>
        </div>
        <div className="max-h-64 overflow-auto lg:max-h-none">
          {sessions.length === 0 ? (
            <p className="px-3 py-3 text-xs text-zinc-500">No sessions yet.</p>
          ) : (
            <ul className="divide-y divide-zinc-800">
              {sessions.map((s) => (
                <li key={s.id} className="flex items-center gap-1">
                  <button
                    type="button"
                    className={`flex-1 truncate px-3 py-2 text-left text-sm hover:bg-zinc-800/60 ${
                      activeSessionId === s.id ? "bg-zinc-800 text-white" : "text-zinc-300"
                    }`}
                    title={s.title}
                    onClick={() => void loadSession(s.id)}
                  >
                    {s.title}
                  </button>
                  <button
                    type="button"
                    className="px-2 text-xs text-zinc-500 hover:text-red-300"
                    aria-label="Delete session"
                    onClick={() => void onDeleteSession(s.id)}
                  >
                    ×
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </aside>

      <section className="flex min-h-[420px] flex-1 flex-col rounded-lg border border-zinc-800 bg-zinc-900/30">
        <header className="border-b border-zinc-800 px-4 py-3">
          <h2 className="text-lg font-semibold">Chat</h2>
          <p className="text-xs text-zinc-500">
            {title} · Answers cite uploads; expand <span className="text-zinc-400">Sources</span>{" "}
            to verify.
          </p>
        </header>

        <div className="flex-1 space-y-3 overflow-auto px-4 py-4">
          {error ? (
            <div className="rounded-md border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-200">
              {error}
            </div>
          ) : null}

          {messages.length === 0 ? (
            <p className="text-sm text-zinc-500">
              Ask a question about your indexed documents. Upload files on the Documents page
              first.
            </p>
          ) : (
            messages.map((m) => {
              const assistantFmt =
                m.role === "assistant" ? formatAssistantReplyForDisplay(m.content) : null;
              return (
                <div
                  key={m.id}
                  className={`max-w-[90%] rounded-lg px-3 py-2 text-sm leading-relaxed ${
                    m.role === "user"
                      ? "ml-auto bg-zinc-800 text-zinc-100"
                      : "mr-auto border border-zinc-700 bg-zinc-950/60 text-zinc-100"
                  }`}
                >
                  {assistantFmt ? (
                    <>
                      {assistantFmt.hadIndexedPrefix ? (
                        <p className="mb-2 border-l-2 border-emerald-500/50 pl-2 text-[11px] leading-snug text-zinc-500">
                          From your indexed documents
                          {m.citations && m.citations.length > 0 ? (
                            <span className="text-zinc-600">
                              {" "}
                              · refs{" "}
                              {m.citations.map((_, i) => (
                                <sup
                                  key={`${m.id}-ref-${i}`}
                                  className="ml-0.5 font-mono text-[10px] text-emerald-500/90"
                                >
                                  [{i + 1}]
                                </sup>
                              ))}
                            </span>
                          ) : null}
                        </p>
                      ) : null}
                      <div className="whitespace-pre-wrap text-[15px] leading-relaxed tracking-tight text-zinc-100">
                        {assistantFmt.body}
                      </div>
                      {m.citations && m.citations.length > 0 ? (
                        <ChatSources citations={m.citations} />
                      ) : null}
                    </>
                  ) : (
                    <div className="whitespace-pre-wrap">{m.content}</div>
                  )}
                </div>
              );
            })
          )}
        </div>

        <form className="border-t border-zinc-800 p-3" onSubmit={onSend}>
          <div className="flex gap-2">
            <textarea
              className="min-h-[44px] flex-1 resize-y rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100 outline-none ring-emerald-500/30 focus:ring-2"
              placeholder="Ask something grounded in your documents… (Enter to send, Shift+Enter for newline)"
              value={input}
              rows={2}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.nativeEvent.isComposing) return;
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  void submitChat();
                }
              }}
            />
            <button
              type="submit"
              disabled={busy}
              className="self-end rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {busy ? "…" : "Send"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
