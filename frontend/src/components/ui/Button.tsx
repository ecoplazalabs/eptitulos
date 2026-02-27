import type { ButtonHTMLAttributes } from 'react';
import { cn } from '@/lib/cn';
import Spinner from '@/components/ui/Spinner';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  fullWidth?: boolean;
  /** Reserved for future slot/asChild pattern. Currently unused. */
  asChild?: boolean;
}

export default function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  fullWidth = false,
  asChild: _asChild,
  disabled,
  className,
  children,
  ...props
}: ButtonProps) {
  const isDisabled = disabled || loading;

  return (
    <button
      disabled={isDisabled}
      aria-busy={loading}
      className={cn(
        'relative inline-flex items-center justify-center gap-2 rounded-lg font-medium',
        'transition-colors duration-200',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-brand-500',
        'disabled:pointer-events-none disabled:opacity-50',
        // variants
        variant === 'primary' && [
          'bg-brand-600 text-white',
          'hover:bg-brand-700 active:bg-brand-800',
        ],
        variant === 'secondary' && [
          'border border-slate-200 bg-white text-slate-700',
          'hover:bg-slate-50 hover:border-slate-300 active:bg-slate-100',
        ],
        variant === 'danger' && [
          'bg-red-600 text-white',
          'hover:bg-red-700 active:bg-red-800',
        ],
        variant === 'ghost' && [
          'bg-transparent text-slate-600',
          'hover:bg-slate-100 hover:text-slate-900 active:bg-slate-200',
        ],
        // sizes
        size === 'sm' && 'h-8 px-3 text-sm',
        size === 'md' && 'h-10 px-4 text-sm',
        size === 'lg' && 'h-11 px-6 text-base',
        // full width
        fullWidth && 'w-full',
        className,
      )}
      {...props}
    >
      {loading && (
        <Spinner
          size="sm"
          className={cn(
            variant === 'primary' && 'text-white',
            variant === 'danger' && 'text-white',
            variant === 'secondary' && 'text-slate-500',
            variant === 'ghost' && 'text-slate-500',
          )}
        />
      )}
      {children}
    </button>
  );
}
