import { type KeyboardEvent } from 'react';
import { useNavigate } from 'react-router';
import Card from '@/components/ui/Card';
import AnalysisStatusBadge from '@/components/analysis/AnalysisStatusBadge';
import { formatRelativeTime, formatDuration } from '@/lib/format';
import { cn } from '@/lib/cn';
import type { AnalysisSummary } from '@/types/analysis';

interface AnalysisCardProps {
  analysis: AnalysisSummary;
}

export default function AnalysisCard({ analysis }: AnalysisCardProps) {
  const navigate = useNavigate();

  const handleClick = () => {
    void navigate(`/analyses/${analysis.id}`);
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      void navigate(`/analyses/${analysis.id}`);
    }
  };

  return (
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
          <AnalysisStatusBadge status={analysis.status} />
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
  );
}
