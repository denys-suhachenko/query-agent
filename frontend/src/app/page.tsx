import { AgentQuery } from '@/features/query-agent/ui/AgentQuery';
import { Container } from '@/shared/layout/Container';

export default function Home() {
  return (
    <Container className="min-h-screen max-w-5xl py-10">
      <AgentQuery />
    </Container>
  );
}
