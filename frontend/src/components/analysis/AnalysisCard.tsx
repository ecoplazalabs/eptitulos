import { useState, type KeyboardEvent } from 'react';
import { useNavigate } from 'react-router';
import Card from '@/components/ui/Card';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import AnalysisStatusBadge from '@/components/analysis/AnalysisStatusBadge';
import { formatRelativeTime, formatDuration } from '@/lib/format';
import { cn } from '@/lib/cn';
import { useDeleteAnalysis } from '@/hooks/useDeleteAnalysis';
import type { AnalysisSummary } from '@/types/analysis';

interface AnalysisCardProps {
  analysis: AnalysisSummary;
}

export default function AnalysisCard({ analysis }: AnalysisCardProps) {
  const navigate = useNavigate();
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const deleteMutation = useDeleteAnalysis(analysis.id);

  const handleClick = () => {
    void navigate(`/analyses/${analysis.id}`);
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      void navigate(`/analyses/${analysis.id}`);
    }
  };

  const handleDeleteClick = (e: React.MouseEvent) => {
    // Prevent the card navigation from triggering
    e.stopPropagation();
    setShowDeleteDialog(true);
  };

  const handleConfirmDelete = () => {
    deleteMutation.mutate(undefined, {
      onSuccess: () => setShowDeleteDialog(false),
      onError: () => setShowDeleteDialog(false),
    });
  };

  const canDelete = analysis.status === 'failed';

  return (
    <>
      <Card
        padding="sm"
        role="button"
        tabIndex={0}
        aria-label={`Ver analisis de partida ${analysis.partida} en ${analysis.oficina}`}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        className={cn(
          'cursor-pointer select-none transition-all duration-150',
          'hover:border-slate-300 hover:shadow-md',
          'active:scale-[0.99]',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2',
        )}
      >
        <div className="flex flex-col gap-3">
          {/* Header row */}
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold text-slate-900">
                Partida {analysis.partida}
              </p>
              <p className="mt-0.5 text-xs text-slate-500">{analysis.oficina}</p>
            </div>
            <div className="flex shrink-0 items-center gap-2">
              <AnalysisStatusBadge status={analysis.status} />
              {canDelete && (
                <button
                  type="button"
                  aria-label="Eliminar analisis fallido"
                  title="Eliminar"
                  onClick={handleDeleteClick}
                  className={cn(
                    'flex size-6 items-center justify-center rounded-md',
                    'text-slate-300 transition-colors duration-150',
                    'hover:bg-red-50 hover:text-red-500',
                    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-400 focus-visible:ring-offset-1',
                  )}
                >
                  {/* Minimal trash icon via SVG — no new dependency */}
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 16 16"
                    fill="currentColor"
                    className="size-3.5"
                    aria-hidden="true"
                  >
                    <path
                      fillRule="evenodd"
                      d="M5 3.25V4H2.75a.75.75 0 0 0 0 1.5h.3l.815 8.15A1.5 1.5 0 0 0 5.357 15h5.285a1.5 1.5 0 0 0 1.493-1.35l.815-8.15h.3a.75.75 0 0 0 0-1.5H11v-.75A2.25 2.25 0 0 0 8.75 1h-1.5A2.25 2.25 0 0 0 5 3.25Zm2.25-.75a.75.75 0 0 0-.75.75V4h3v-.75a.75.75 0 0 0-.75-.75h-1.5ZM6.05 6a.75.75 0 0 1 .787.713l.275 5.5a.75.75 0 0 1-1.498.075l-.275-5.5A.75.75 0 0 1 6.05 6Zm3.9 0a.75.75 0 0 1 .712.787l-.275 5.5a.75.75 0 0 1-1.498-.075l.275-5.5a.75.75 0 0 1 .786-.711Z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
              )}
            </div>
          </div>

          {/* Footer row */}
          <div className="flex items-center gap-3 text-xs text-slate-400">
            <span>{formatRelativeTime(analysis.created_at)}</span>

            {analysis.duration_seconds != null && (
              <>
                <span aria-hidden>·</span>
                <span>{formatDuration(analysis.duration_seconds)}</span>
              </>
            )}

            {analysis.status === 'completed' && (
              <>
                <span aria-hidden>·</span>
                <span>
                  {analysis.cargas_count === 0
                    ? 'Sin cargas'
                    : `${analysis.cargas_count} carga${analysis.cargas_count !== 1 ? 's' : ''}`}
                </span>
              </>
            )}
          </div>
        </div>
      </Card>

      <ConfirmDialog
        open={showDeleteDialog}
        variant="danger"
        title="Eliminar analisis"
        description={`Se eliminara permanentemente el analisis de la partida ${analysis.partida}. No podras recuperarlo despues.`}
        confirmLabel="Si, eliminar"
        cancelLabel="Volver"
        loading={deleteMutation.isPending}
        onConfirm={handleConfirmDelete}
        onCancel={() => setShowDeleteDialog(false)}
      />
    </>
  );
}
