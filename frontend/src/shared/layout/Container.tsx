import { ComponentPropsWithoutRef, ElementType } from 'react';

import { cn } from '@/shared/lib/utils';

type ContainerProps<T extends ElementType = 'div'> = {
  as?: T;
  className?: string;
  children: React.ReactNode;
} & Omit<ComponentPropsWithoutRef<T>, 'as' | 'children' | 'className'>;

export function Container<T extends ElementType = 'div'>({
  as,
  children,
  className,
  ...props
}: ContainerProps<T>) {
  const Component = as || 'div';

  return (
    <Component
      className={cn('mx-auto w-full max-w-6xl px-6 lg:px-8 xl:px-6', className)}
      {...props}
    >
      {children}
    </Component>
  );
}
