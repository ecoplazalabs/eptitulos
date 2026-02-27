import { Link, useParams, useNavigate } from 'react-router';
import Button from '@/components/ui/Button';
import Alert from '@/components/ui/Alert';
import Spinner from '@/components/ui/Spinner';
import AnalysisProgress from '@/components/analysis/AnalysisProgress';
import AnalysisResult from '@/components/analysis/AnalysisResult';
import AnalysisStatusBadge from '@/components/analysis/AnalysisStatusBadge';
import { useAnalysis } from '@/hooks/useAnalysis';

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

  const { data: analysis, isLoading, isError, error } = useAnalysis(id ?? '');

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

  return (
    <div className="flex flex-col gap-6">
      {/* Breadcrumb */}
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

      {/* Content based on status */}
      {(analysis.status === 'pending' || analysis.status === 'processing') && (
        <AnalysisProgress analysis={analysis} />
      )}

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
  );
}
