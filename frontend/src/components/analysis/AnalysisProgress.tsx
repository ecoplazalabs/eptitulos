import { useState, useEffect, useRef } from 'react';
import Spinner from '@/components/ui/Spinner';
import { formatDuration } from '@/lib/format';
import type { Analysis } from '@/types/analysis';

interface AnalysisProgressProps {
  analysis: Pick<Analysis, 'status' | 'partida' | 'oficina' | 'created_at' | 'progress_log'>;
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

function classifyLine(line: string): 'error' | 'success' | 'normal' {
  if (/error|fail|exception|timeout/i.test(line)) return 'error';
  if (/complet|exitos|finaliz|descarg.*ok/i.test(line)) return 'success';
  return 'normal';
}

const LINE_COLORS: Record<string, string> = {
  error: 'text-red-400',
  success: 'text-emerald-400',
  normal: 'text-slate-400',
};

function ProgressLog({ log }: { log: string }) {
  const [isOpen, setIsOpen] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const lines = log.split('\n').filter(Boolean);

  useEffect(() => {
    if (isOpen && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [isOpen, log]);

  if (lines.length === 0) return null;

  return (
    <div className="w-full max-w-lg">
      <button
        type="button"
        onClick={() => { setIsOpen(!isOpen); }}
        className="flex w-full items-center justify-between rounded-lg border border-slate-200 bg-slate-50 px-4 py-2.5 text-left text-sm transition-colors hover:bg-slate-100"
      >
        <span className="font-medium text-slate-700">
          {isOpen ? 'Ocultar' : 'Ver'} actividad del agente
          <span className="ml-1.5 text-slate-400">({lines.length} eventos)</span>
        </span>
        <svg
          className={`size-4 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={2}
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="m19 9-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div
          ref={scrollRef}
          className="mt-2 max-h-64 overflow-y-auto rounded-lg bg-slate-950 p-4 font-mono text-xs leading-relaxed"
        >
          {lines.map((line, i) => {
            const kind = classifyLine(line);
            return (
              <div key={i} className={LINE_COLORS[kind]}>
                {line}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

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

      {/* Progress log viewer */}
      {analysis.progress_log && <ProgressLog log={analysis.progress_log} />}
    </div>
  );
}
