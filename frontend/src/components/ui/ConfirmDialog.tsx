import { useEffect, useRef } from 'react';
import { cn } from '@/lib/cn';
import Button from '@/components/ui/Button';

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: 'danger' | 'primary';
  loading?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmDialog({
  open,
  title,
  description,
  confirmLabel = 'Confirmar',
  cancelLabel = 'Cancelar',
  variant = 'danger',
  loading = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const cancelRef = useRef<HTMLButtonElement>(null);

  // Focus the cancel button when the dialog opens (safe default)
  useEffect(() => {
    if (open) {
      cancelRef.current?.focus();
    }
  }, [open]);

  // Close on Escape
  useEffect(() => {
    if (!open) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onCancel();
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [open, onCancel]);

  if (!open) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-dialog-title"
      aria-describedby="confirm-dialog-description"
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        aria-hidden="true"
        onClick={onCancel}
      />

      {/* Panel */}
      <div
        className={cn(
          'relative z-10 w-full max-w-sm rounded-2xl bg-white shadow-xl',
          'border border-slate-200',
          'flex flex-col gap-5 p-6',
        )}
      >
        {/* Icon + title */}
        <div className="flex flex-col gap-2">
          <div
            className={cn(
              'flex size-10 items-center justify-center rounded-full',
              variant === 'danger' && 'bg-red-50',
              variant === 'primary' && 'bg-brand-50',
            )}
            aria-hidden="true"
          >
            <span
              className={cn(
                'text-lg',
                variant === 'danger' && 'text-red-600',
                variant === 'primary' && 'text-brand-600',
              )}
            >
              {variant === 'danger' ? '!' : '?'}
            </span>
          </div>

          <h2
            id="confirm-dialog-title"
            className="text-base font-semibold text-slate-900"
          >
            {title}
          </h2>
          <p
            id="confirm-dialog-description"
            className="text-sm text-slate-500 leading-relaxed"
          >
            {description}
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-3 justify-end">
          <Button
            ref={cancelRef}
            variant="secondary"
            size="sm"
            disabled={loading}
            onClick={onCancel}
          >
            {cancelLabel}
          </Button>
          <Button
            variant={variant}
            size="sm"
            loading={loading}
            onClick={onConfirm}
          >
            {confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  );
}
