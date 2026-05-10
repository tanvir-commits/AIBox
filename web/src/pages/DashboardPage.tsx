import { SystemStatusPanel } from "../components/SystemStatusPanel";

export function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold">Dashboard</h2>
        <p className="mt-1 text-sm text-zinc-400">
          Overview of stack health and providers.
        </p>
      </div>
      <SystemStatusPanel />
    </div>
  );
}
