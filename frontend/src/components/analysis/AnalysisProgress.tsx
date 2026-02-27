import { useState, useEffect } from 'react';
import Spinner from '@/components/ui/Spinner';
import { formatDuration } from '@/lib/format';
import type { Analysis } from '@/types/analysis';

interface AnalysisProgressProps {
  analysis: Pick<Analysis, 'status' | 'partida' | 'oficina' | 'created_at'>;
}

function useElapsedSeconds(startDateString: string): number {
  const [elapsed, setElapsed] = useState(() => {
    return Math.floor((Date.now() - new Date(startDateString).getTime()) / 1000);
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed(Math.floor((Date.now() - new Date(startDateString).getTime()) / 1000));
    }, 1000);

    return () => clearInterval(interval);
  }, [startDateString]);

  return elapsed;
}

const STATUS_MESSAGE: Record<string, string> = {
  pending: 'Solicitud recibida, en cola de procesamiento...',
  processing: 'Consultando SUNARP y analizando la partida...',
};

export default function AnalysisProgress({ analysis }: AnalysisProgressProps) {
  const elapsed = useElapsedSeconds(analysis.created_at);
  const statusMessage = STATUS_MESSAGE[analysis.status] ?? 'Procesando...';

  return (
    <div className="flex flex-col items-center gap-8 py-12 text-center">
      {/* Animated icon */}
      <div className="relative flex items-center justify-center">
        <span
          className="absolute size-24 animate-ping rounded-full bg-brand-100 opacity-60"
          aria-hidden
        />
        <span
          className="absolute size-16 animate-ping rounded-full bg-brand-200 opacity-40 [animation-delay:0.3s]"
          aria-hidden
        />
        <div className="relative flex size-20 items-center justify-center rounded-full bg-brand-50 ring-1 ring-brand-200">
          <Spinner size="lg" className="text-brand-600" />
        </div>
      </div>

      {/* Heading */}
      <div className="flex flex-col gap-2">
        <h2 className="text-xl font-semibold text-slate-900">
          Analizando partida {analysis.partida}
        </h2>
        <p className="text-sm text-slate-500">{analysis.oficina}</p>
      </div>

      {/* Status message */}
      <p className="max-w-sm text-sm text-slate-600">{statusMessage}</p>

      {/* Time info */}
      <div className="flex flex-col items-center gap-1">
        <p className="text-2xl font-mono font-semibold text-slate-800" aria-live="polite" aria-atomic>
          {formatDuration(elapsed)}
        </p>
        <p className="text-xs text-slate-400">Tiempo estimado: 3-8 minutos</p>
      </div>

      {/* Progress dots */}
      <div className="flex gap-1.5" aria-hidden>
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="size-1.5 rounded-full bg-brand-400 animate-bounce"
            style={{ animationDelay: `${i * 0.15}s` }}
          />
        ))}
      </div>
    </div>
  );
}
