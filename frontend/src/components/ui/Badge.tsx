import type { HTMLAttributes } from 'react';
import { cn } from '@/lib/cn';

type BadgeVariant = 'success' | 'warning' | 'danger' | 'info' | 'neutral' | 'default' | 'error';

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
}

const VARIANT_CLASSES: Record<BadgeVariant, string> = {
  success: 'bg-green-100 text-green-700',
  warning: 'bg-amber-100 text-amber-700',
  danger: 'bg-red-100 text-red-700',
  // 'error' is an alias for 'danger'
  error: 'bg-red-100 text-red-700',
  info: 'bg-brand-100 text-brand-700',
  neutral: 'bg-slate-100 text-slate-600',
  // 'default' is an alias for 'neutral'
  default: 'bg-slate-100 text-slate-600',
};

export default function Badge({
  variant = 'neutral',
  className,
  children,
  ...props
}: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        VARIANT_CLASSES[variant],
        className,
      )}
      {...props}
    >
      {children}
    </span>
  );
}
