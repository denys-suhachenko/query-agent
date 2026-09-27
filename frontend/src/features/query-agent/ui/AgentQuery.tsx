'use client';

import { useState } from 'react';
import { SparklesIcon, XIcon } from 'lucide-react';

import { Button } from '@/shared/ui/button';
import {
  InputGroup,
  InputGroupAddon,
  InputGroupButton,
  InputGroupInput,
} from '@/shared/ui/input-group';

import { streamAgentQuery } from '@/features/query-agent/api/api';
import type {
  AgentQueryResponse,
  AgentStage,
} from '@/features/query-agent/model/types';
import { cn } from '@/shared/lib/utils';

import { EmptyState } from './EmptyState';
import { AgentQuerySkeleton } from './AgentQuerySkeleton';
import { SqlExecution } from './SqlExecution';
import { AgentAnswer } from './AgentAnswer';

export function AgentQuery() {
  const [message, setMessage] = useState('');
  const [result, setResult] = useState<AgentQueryResponse | null>(null);

  const [activity, setActivity] = useState<{
    stage: AgentStage;
    message: string;
  } | null>(null);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.BaseSyntheticEvent) {
    event.preventDefault();

    const trimmedMessage = message.trim();

    if (!trimmedMessage || isLoading) {
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    setActivity({
      stage: 'analysis',
      message: 'Starting analysis',
    });

    try {
      await streamAgentQuery(
        {
          message: trimmedMessage,
        },
        (event) => {
          switch (event.type) {
            case 'activity':
              setActivity({
                stage: event.stage,
                message: event.message,
              });
              break;

            case 'result':
              setResult(event.data);
              break;

            case 'done':
              setActivity(null);
              break;

            case 'error':
              setError(event.message);
              break;
          }
        },
      );
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Something went wrong');
    } finally {
      setIsLoading(false);
      setActivity(null);
    }
  }

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-6">
      <form onSubmit={handleSubmit} className="flex items-center gap-2">
        <InputGroup className="h-12 border border-neutral-200 bg-white p-2 shadow-xs">
          <InputGroupInput
            value={message}
            placeholder="Write a message..."
            autoComplete="off"
            className={cn(
              'appearance-none rounded-lg md:text-base',
              '[&:-webkit-autofill]:shadow-[0_0_0_1000px_white_inset]',
              '[&:-webkit-autofill]:[-webkit-text-fill-color:inherit]',
            )}
            onChange={(event) => setMessage(event.target.value)}
          />
          <InputGroupAddon align="inline-end">
            {message.trim() && (
              <Button
                size="icon"
                variant="ghost"
                className="rounded-full"
                onClick={() => setMessage('')}
              >
                <XIcon className="size-5" />
              </Button>
            )}
            <InputGroupButton
              type="submit"
              variant="default"
              disabled={isLoading || !message.trim()}
              className="flex h-8 items-center gap-2 rounded-md px-4"
            >
              <SparklesIcon className="size-4" />
              {isLoading ? 'Analyzing...' : 'Ask AI'}
            </InputGroupButton>
          </InputGroupAddon>
        </InputGroup>
      </form>

      {isLoading && activity && (
        <p className="shimmer text-muted-foreground shimmer-duration-1500 text-sm font-medium">
          {activity?.message}
        </p>
      )}

      {!result && !isLoading && <EmptyState />}

      <>
        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {isLoading && <AgentQuerySkeleton />}

        {result && (
          <div className="flex flex-col gap-6">
            {result.sql_executions.length > 0 && (
              <section className="space-y-3">
                {result.sql_executions.map((execution, index) => (
                  <SqlExecution
                    key={`${index}-${execution.sql}`}
                    execution={execution}
                    index={index}
                  />
                ))}
              </section>
            )}

            <AgentAnswer answer={result.answer} />
          </div>
        )}
      </>
    </div>
  );
}
