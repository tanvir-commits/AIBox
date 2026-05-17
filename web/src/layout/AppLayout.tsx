import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const nav = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/chat", label: "Chat" },
  { to: "/documents", label: "Documents" },
  { to: "/sources", label: "Sources" },
  { to: "/models", label: "Models" },
  { to: "/system", label: "System" },
  { to: "/settings", label: "Settings" },
];

export function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen bg-zinc-950 text-zinc-100">
      <aside className="flex w-56 flex-col border-r border-zinc-800 bg-zinc-900/60">
        <div className="border-b border-zinc-800 px-4 py-4">
          <div className="flex items-center gap-2.5">
            <img
              src="/logo.svg"
              alt=""
              className="h-8 w-8 shrink-0 rounded-lg"
              width={32}
              height={32}
            />
            <div className="min-w-0">
              <div className="text-sm font-semibold tracking-tight leading-tight">
                <span className="text-zinc-400">Local </span>
                <span className="text-emerald-400">AI </span>
                <span className="text-zinc-100">Box</span>
              </div>
              <div className="truncate text-xs text-zinc-500">{user?.email}</div>
            </div>
          </div>
        </div>
        <nav className="flex flex-1 flex-col gap-0.5 p-2">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                [
                  "rounded-md px-3 py-2 text-sm transition-colors",
                  isActive
                    ? "bg-zinc-800 text-white"
                    : "text-zinc-400 hover:bg-zinc-800/60 hover:text-zinc-100",
                ].join(" ")
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-zinc-800 p-2">
          <button
            type="button"
            className="w-full rounded-md px-3 py-2 text-left text-sm text-zinc-400 hover:bg-zinc-800/60 hover:text-zinc-100"
            onClick={async () => {
              await logout();
              navigate("/login", { replace: true });
            }}
          >
            Log out
          </button>
        </div>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="border-b border-zinc-800 bg-zinc-900/40 px-8 py-4">
          <h1 className="text-lg font-medium text-zinc-100">Console</h1>
          <p className="text-sm text-zinc-500">
            Phase 1 shell — navigation and placeholders; Phase 2 auth enabled.
          </p>
        </header>
        <main className="flex-1 overflow-auto px-8 py-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
