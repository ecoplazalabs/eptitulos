import { useState } from 'react';
import { Link } from 'react-router';
import Button from '@/components/ui/Button';
import Alert from '@/components/ui/Alert';
import Card from '@/components/ui/Card';
import AnalysisCard from '@/components/analysis/AnalysisCard';
import { useAnalyses } from '@/hooks/useAnalyses';
import { ANALYSES_PER_PAGE } from '@/lib/constants';

function SkeletonCard() {
  return (
    <Card padding="sm" className="animate-pulse">
      <div className="flex flex-col gap-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 space-y-2">
            <div className="h-4 w-32 rounded bg-slate-200" />
            <div className="h-3 w-20 rounded bg-slate-100" />
          </div>
          <div className="h-5 w-20 rounded-full bg-slate-200" />
        </div>
        <div className="flex gap-3">
          <div className="h-3 w-24 rounded bg-slate-100" />
          <div className="h-3 w-16 rounded bg-slate-100" />
        </div>
      </div>
    </Card>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center gap-4 py-16 text-center">
      <div className="flex size-16 items-center justify-center rounded-full bg-slate-100">
        <span className="text-2xl" aria-hidden>
          📋
        </span>
      </div>
      <div className="flex flex-col gap-1">
        <p className="text-base font-semibold text-slate-800">No tienes analisis aun</p>
        <p className="max-w-xs text-sm text-slate-500">
          Solicita el analisis de una partida registral de SUNARP para comenzar.
        </p>
      </div>
      <Link to="/analyses/new">
        <Button size="md">
          <span aria-hidden>+</span>
          Nuevo Analisis
        </Button>
      </Link>
    </div>
  );
}

export default function DashboardPage() {
  const [page, setPage] = useState(1);
  const { data, isLoading, isError, error } = useAnalyses({ page, perPage: ANALYSES_PER_PAGE });

  const analyses = data?.data ?? [];
  const totalPages = data ? Math.ceil(data.pagination.total / data.pagination.per_page) : 0;
  const totalItems = data?.pagination.total ?? 0;

  const hasPreviousPage = page > 1;
  const hasNextPage = page < totalPages;

  return (
    <div className="flex flex-col gap-6">
      {/* Page header */}
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Mis Analisis</h1>
          {!isLoading && totalItems > 0 && (
            <p className="mt-0.5 text-sm text-slate-500">
              {totalItems} analisis en total
            </p>
          )}
        </div>
        <Link to="/analyses/new">
          <Button size="md">
            <span aria-hidden>+</span>
            Nuevo Analisis
          </Button>
        </Link>
      </div>

      {/* Error state */}
      {isError && (
        <Alert variant="error" title="No se pudieron cargar los analisis">
          {(error as { message?: string })?.message ?? 'Ocurrio un error inesperado.'}
        </Alert>
      )}

      {/* Loading state */}
      {isLoading && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3" aria-busy aria-label="Cargando analisis">
          {Array.from({ length: 6 }, (_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      )}

      {/* Empty state */}
      {!isLoading && !isError && analyses.length === 0 && <EmptyState />}

      {/* Analyses list */}
      {!isLoading && analyses.length > 0 && (
        <>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {analyses.map((analysis) => (
              <AnalysisCard key={analysis.id} analysis={analysis} />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between gap-4 pt-2">
              <p className="text-sm text-slate-500">
                Pagina {page} de {totalPages}
              </p>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={!hasPreviousPage}
                  onClick={() => setPage((p) => p - 1)}
                >
                  Anterior
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={!hasNextPage}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Siguiente
                </Button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
