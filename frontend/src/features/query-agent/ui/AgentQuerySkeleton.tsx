export function AgentQuerySkeleton() {
  return (
    <div className="space-y-y animate-pulse rounded-lg border border-neutral-200 bg-white p-6 shadow-xs">
      <div className="h-6 w-48 rounded bg-neutral-200" />

      <div className="mt-4 space-y-3">
        <div className="h-5 w-full rounded bg-neutral-100" />
        <div className="h-5 w-5/6 rounded bg-neutral-100" />
        <div className="h-5 w-2/3 rounded bg-neutral-100" />
      </div>
    </div>
  );
}
