import type { HTMLAttributes, ReactNode } from 'react';
import { cn } from '@/lib/cn';

type AlertVariant = 'info' | 'success' | 'warning' | 'error';

interface AlertProps extends HTMLAttributes<HTMLDivElement> {
  variant?: AlertVariant;
  title?: string;
  children?: ReactNode;
}

interface VariantConfig {
  containerClasses: string;
  icon: string;
  iconClasses: string;
}

const VARIANT_CONFIG: Record<AlertVariant, VariantConfig> = {
  info: {
    containerClasses: 'border-brand-200 bg-brand-50 text-brand-800',
    icon: 'ℹ',
    iconClasses: 'text-brand-500',
  },
  success: {
    containerClasses: 'border-green-200 bg-green-50 text-green-800',
    icon: '✓',
    iconClasses: 'text-green-500',
  },
  warning: {
    containerClasses: 'border-amber-200 bg-amber-50 text-amber-800',
    icon: '⚠',
    iconClasses: 'text-amber-500',
  },
  error: {
    containerClasses: 'border-red-200 bg-red-50 text-red-800',
    icon: '✕',
    iconClasses: 'text-red-500',
  },
};

export default function Alert({
  variant = 'info',
  title,
  className,
  children,
  ...props
}: AlertProps) {
  const config = VARIANT_CONFIG[variant];

  return (
    <div
      role="alert"
      className={cn(
        'flex gap-3 rounded-lg border px-4 py-3',
        config.containerClasses,
        className,
      )}
      {...props}
    >
      <span
        className={cn('mt-0.5 shrink-0 text-sm font-bold leading-none', config.iconClasses)}
        aria-hidden="true"
      >
        {config.icon}
      </span>
      <div className="min-w-0 flex-1">
        {title && (
          <p className="text-sm font-semibold leading-5">{title}</p>
        )}
        {children && (
          <p className={cn('text-sm leading-5', title && 'mt-0.5 opacity-90')}>
            {children}
          </p>
        )}
      </div>
    </div>
  );
}
