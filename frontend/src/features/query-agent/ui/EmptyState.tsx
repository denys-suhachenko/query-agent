import Image from 'next/image';

export function EmptyState() {
  return (
    <div className="w-full min-w-0 flex-1 flex-col items-center justify-center gap-4 rounded-lg border border-neutral-200 bg-white px-6 py-8 shadow-xs">
      <div
        className="mx-auto mb-4"
        style={{
          width: 'clamp(80px,35%,240px)',
        }}
      >
        <Image
          src="/query-assistant.webp"
          alt="Query Assistant"
          loading="eager"
          width={240}
          height={240}
        />
      </div>
      <div className="text-center text-balance">
        <h3 className="text-3xl font-semibold">Hello. How can I help you?</h3>
        <p className="mt-2 text-lg font-medium text-gray-500">
          I&apos;m AI assistant for SQL queries building.
        </p>
      </div>
    </div>
  );
}
