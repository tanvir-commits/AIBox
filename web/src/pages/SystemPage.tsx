import { SystemStatusPanel } from "../components/SystemStatusPanel";

export function SystemPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold">System</h2>
        <p className="mt-1 text-sm text-zinc-400">
          Service health, databases, and model providers.
        </p>
      </div>
      <SystemStatusPanel />
    </div>
  );
}
