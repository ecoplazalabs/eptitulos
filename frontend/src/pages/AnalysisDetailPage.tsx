import { useState } from 'react';
import { Link, useParams, useNavigate } from 'react-router';
import Button from '@/components/ui/Button';
import Alert from '@/components/ui/Alert';
import Spinner from '@/components/ui/Spinner';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import AnalysisProgress from '@/components/analysis/AnalysisProgress';
import AnalysisResult from '@/components/analysis/AnalysisResult';
import AnalysisStatusBadge from '@/components/analysis/AnalysisStatusBadge';
import { useAnalysis } from '@/hooks/useAnalysis';
import { useCancelAnalysis } from '@/hooks/useCancelAnalysis';
import { useDeleteAnalysis } from '@/hooks/useDeleteAnalysis';

function LoadingState() {
  return (
    <div className="flex items-center justify-center py-24">
      <Spinner size="lg" className="text-brand-600" />
    </div>
  );
}

export default function AnalysisDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [showCancelDialog, setShowCancelDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  const { data: analysis, isLoading, isError, error } = useAnalysis(id ?? '');

  const cancelMutation = useCancelAnalysis(id ?? '');
  const deleteMutation = useDeleteAnalysis(id ?? '');

  const handleConfirmCancel = () => {
    cancelMutation.mutate(undefined, {
      onSuccess: () => setShowCancelDialog(false),
      onError: () => setShowCancelDialog(false),
    });
  };

  const handleConfirmDelete = () => {
    deleteMutation.mutate(undefined, {
      onSuccess: () => void navigate('/dashboard'),
      onError: () => setShowDeleteDialog(false),
    });
  };

  if (!id) {
    return (
      <Alert variant="error" title="ID de analisis no encontrado">
        La URL no contiene un ID de analisis valido.
      </Alert>
    );
  }

  if (isLoading) {
    return <LoadingState />;
  }

  if (isError) {
    const axiosError = error as { response?: { status?: number } };
    const is404 = axiosError.response?.status === 404;

    return (
      <div className="flex flex-col gap-4">
        <Alert
          variant="error"
          title={is404 ? 'Analisis no encontrado' : 'Error al cargar el analisis'}
        >
          {is404
            ? 'El analisis que buscas no existe o no tienes permisos para verlo.'
            : 'Ocurrio un error al cargar los datos. Intenta de nuevo.'}
        </Alert>
        <Link to="/dashboard">
          <Button variant="secondary" size="sm">
            Volver al Dashboard
          </Button>
        </Link>
      </div>
    );
  }

  if (!analysis) return null;

  const isInProgress =
    analysis.status === 'pending' || analysis.status === 'processing';
  const isDone =
    analysis.status === 'completed' || analysis.status === 'failed';

  return (
    <>
      <div className="flex flex-col gap-6">
        {/* Breadcrumb + actions row */}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <nav aria-label="Breadcrumb">
            <ol className="flex flex-wrap items-center gap-1.5 text-sm text-slate-500">
              <li>
                <Link
                  to="/dashboard"
                  className="hover:text-slate-700 focus-visible:outline-none focus-visible:underline"
                >
                  Dashboard
                </Link>
              </li>
              <li aria-hidden>
                <span className="text-slate-300">/</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-slate-900">
                  Analisis #{analysis.partida}
                </span>
                <AnalysisStatusBadge status={analysis.status} />
              </li>
            </ol>
          </nav>

          {/* Contextual action buttons */}
          <div className="flex items-center gap-2">
            {isInProgress && (
              <Button
                variant="secondary"
                size="sm"
                className="border-red-200 text-red-600 hover:border-red-300 hover:bg-red-50"
                onClick={() => setShowCancelDialog(true)}
              >
                Cancelar analisis
              </Button>
            )}

            {isDone && (
              <Button
                variant="secondary"
                size="sm"
                className="border-red-200 text-red-600 hover:border-red-300 hover:bg-red-50"
                onClick={() => setShowDeleteDialog(true)}
              >
                Eliminar
              </Button>
            )}
          </div>
        </div>

        {/* Mutation error feedback */}
        {cancelMutation.isError && (
          <Alert variant="error" title="No se pudo cancelar el analisis">
            {(cancelMutation.error as { message?: string })?.message ??
              'Ocurrio un error inesperado. Intenta de nuevo.'}
          </Alert>
        )}

        {deleteMutation.isError && (
          <Alert variant="error" title="No se pudo eliminar el analisis">
            {(deleteMutation.error as { message?: string })?.message ??
              'Ocurrio un error inesperado. Intenta de nuevo.'}
          </Alert>
        )}

        {/* Content based on status */}
        {isInProgress && <AnalysisProgress analysis={analysis} />}

        {analysis.status === 'completed' && (
          <AnalysisResult analysis={analysis} />
        )}

        {analysis.status === 'failed' && (
          <div className="flex flex-col gap-4">
            <Alert variant="error" title="El analisis no pudo completarse">
              {analysis.error_message ??
                'Ocurrio un error durante el procesamiento de la partida. Por favor intenta de nuevo.'}
            </Alert>
            <div className="flex gap-3">
              <Button
                variant="primary"
                size="md"
                onClick={() => void navigate('/analyses/new')}
              >
                Reintentar
              </Button>
              <Link to="/dashboard">
                <Button variant="secondary" size="md">
                  Volver al Dashboard
                </Button>
              </Link>
            </div>
          </div>
        )}
      </div>

      {/* Confirm dialogs — rendered outside the main flow to avoid layout shift */}
      <ConfirmDialog
        open={showCancelDialog}
        variant="danger"
        title="Cancelar analisis"
        description={`Se cancelara el analisis de la partida ${analysis.partida}. Esta accion no se puede deshacer.`}
        confirmLabel="Si, cancelar"
        cancelLabel="Volver"
        loading={cancelMutation.isPending}
        onConfirm={handleConfirmCancel}
        onCancel={() => setShowCancelDialog(false)}
      />

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
