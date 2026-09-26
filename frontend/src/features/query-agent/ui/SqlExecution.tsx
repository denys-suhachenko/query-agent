import { CheckIcon, CodeXmlIcon, CopyIcon } from 'lucide-react';
import type { SqlExecution as SqlExecutionType } from '../model/types';

import { Button } from '@/shared/ui/button';

import { ResultTable } from './ResultTable';
import { useCopyToClipboard } from '@/shared/hooks';

type SqlExecutionProps = {
  execution: SqlExecutionType;
  index: number;
};

export function SqlExecution({ execution }: SqlExecutionProps) {
  const [onClipboardCopy, isCopied] = useCopyToClipboard();

  return (
    <section className="space-y-6 rounded-lg border border-neutral-200 bg-white p-6 shadow-xs">
      <div className="space-y-4">
        <h3 className="font-semibold">Executed SQL</h3>

        <div className="rounded-lg bg-[#282c34]">
          <div className="flex items-center justify-between border-b border-neutral-600 px-5 py-2 text-white">
            <div className="flex flex-1 items-center gap-2">
              <CodeXmlIcon className="size-4" />
              <h4 className="text-sm font-medium">SQL</h4>
            </div>

            <Button
              variant="ghost"
              size="icon-lg"
              className="cursor-pointer rounded-full hover:bg-gray-900 hover:text-current"
              onClick={() => onClipboardCopy(execution.sql)}
            >
              {isCopied ? (
                <CheckIcon className="size-4" />
              ) : (
                <CopyIcon className="size-4" />
              )}
            </Button>
          </div>

          <pre
            dir="ltr"
            className="overflow-x-auto px-5 py-4 text-sm leading-6 text-neutral-50"
          >
            <code>{execution.sql}</code>
          </pre>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="font-semibold">Result</h3>

        <ResultTable columns={execution.columns} rows={execution.rows} />

        {execution.truncated && (
          <p className="text-sm text-amber-600">Result was truncated.</p>
        )}
      </div>
    </section>
  );
}
