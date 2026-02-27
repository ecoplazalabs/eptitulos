import type { HTMLAttributes, MouseEvent, KeyboardEvent } from 'react';
import { cn } from '@/lib/cn';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  padding?: 'none' | 'sm' | 'md' | 'lg';
  variant?: 'default' | 'hoverable';
}

export default function Card({
  padding = 'md',
  variant = 'default',
  className,
  children,
  onClick,
  ...props
}: CardProps) {
  const isClickable = variant === 'hoverable' || typeof onClick === 'function';

  return (
    <div
      role={isClickable ? 'button' : undefined}
      tabIndex={isClickable ? 0 : undefined}
      onClick={onClick}
      onKeyDown={
        isClickable && onClick
          ? (e: KeyboardEvent<HTMLDivElement>) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onClick(e as unknown as MouseEvent<HTMLDivElement>);
              }
            }
          : undefined
      }
      className={cn(
        'rounded-xl border border-slate-200 bg-white shadow-sm',
        // padding
        padding === 'none' && 'p-0',
        padding === 'sm' && 'p-4',
        padding === 'md' && 'p-6',
        padding === 'lg' && 'p-8',
        // hoverable
        isClickable && [
          'cursor-pointer',
          'transition-shadow duration-200',
          'hover:shadow-md',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2',
        ],
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}
