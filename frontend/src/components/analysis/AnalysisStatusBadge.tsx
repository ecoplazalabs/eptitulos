import Badge from '@/components/ui/Badge';
import { cn } from '@/lib/cn';
import { STATUS_LABELS } from '@/lib/constants';
import type { AnalysisStatus } from '@/types/analysis';
import type { ComponentProps } from 'react';

type BadgeVariant = ComponentProps<typeof Badge>['variant'];

const STATUS_VARIANT: Record<AnalysisStatus, BadgeVariant> = {
  pending: 'default',
  processing: 'info',
  completed: 'success',
  failed: 'error',
};

interface AnalysisStatusBadgeProps {
  status: AnalysisStatus;
  className?: string;
}

export default function AnalysisStatusBadge({ status, className }: AnalysisStatusBadgeProps) {
  return (
    <Badge
      variant={STATUS_VARIANT[status]}
      className={cn(status === 'processing' && 'animate-pulse', className)}
    >
      {STATUS_LABELS[status]}
    </Badge>
  );
}
