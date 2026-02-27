import { formatDate } from '@/lib/format';
import { cn } from '@/lib/cn';
import type { Carga } from '@/types/analysis';

interface CargasListProps {
  cargas: Carga[];
}

function CargaIcon({ vigente }: { vigente: boolean }) {
  return (
    <span
      aria-label={vigente ? 'Carga vigente' : 'Carga cancelada'}
      className={cn(
        'mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full text-xs',
        vigente
          ? 'bg-red-100 text-red-600'
          : 'bg-green-100 text-green-600',
      )}
    >
      {vigente ? '!' : '✓'}
    </span>
  );
}

export default function CargasList({ cargas }: CargasListProps) {
  if (cargas.length === 0) {
    return (
      <div className="flex flex-col items-center gap-2 py-8 text-center">
        <span className="text-2xl" aria-hidden>
          ✓
        </span>
        <p className="text-sm font-medium text-slate-600">
          No se encontraron cargas ni gravamenes
        </p>
        <p className="text-xs text-slate-400">La partida esta libre de cargas registrales.</p>
      </div>
    );
  }

  return (
    <ul className="divide-y divide-slate-100" role="list" aria-label="Lista de cargas y gravamenes">
      {cargas.map((carga, index) => (
        <li key={index} className="flex gap-3 py-3 first:pt-0 last:pb-0">
          <CargaIcon vigente={carga.vigente} />
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5">
              <span className="text-sm font-medium text-slate-800">{carga.tipo}</span>
              <span
                className={cn(
                  'text-xs font-medium',
                  carga.vigente ? 'text-red-600' : 'text-green-600',
                )}
              >
                {carga.vigente ? 'Vigente' : 'Cancelada'}
              </span>
            </div>
            <p className="mt-0.5 text-sm text-slate-600">{carga.detalle}</p>
            {carga.fecha && (
              <p className="mt-1 text-xs text-slate-400">
                Fecha: {formatDate(carga.fecha)}
              </p>
            )}
          </div>
        </li>
      ))}
    </ul>
  );
}
