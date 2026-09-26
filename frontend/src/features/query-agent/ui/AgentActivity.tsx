import type { AgentStage } from '../model/types';

type AgentActivityProps = {
  stage: AgentStage;
  message: string;
};

export function AgentActivity({ stage, message }: AgentActivityProps) {
  return (
    <div className="flex items-center gap-3 rounded-xl border border-neutral-200 bg-white px-4 py-3">
      <p className="text-sm font-medium">{message}</p>
    </div>
  );
}
