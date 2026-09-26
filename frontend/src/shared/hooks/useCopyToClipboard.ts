'use client';

import { useRef, useState } from 'react';

export function useCopyToClipboard() {
  const [isCopied, setIsCopied] = useState(false);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  async function onCopy(value: string) {
    if (!value) {
      return;
    }

    try {
      await navigator.clipboard.writeText(value);

      setIsCopied(true);

      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      timeoutRef.current = setTimeout(() => {
        setIsCopied(false);
      }, 2000);
    } catch (error) {
      setIsCopied(false);
      console.log('Failed to copy text: ', error);
    }
  }

  return [onCopy, isCopied] as const;
}
