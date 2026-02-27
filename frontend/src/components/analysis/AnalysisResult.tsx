import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import Alert from '@/components/ui/Alert';
import CargasList from '@/components/analysis/CargasList';
import { usePdfDownload } from '@/hooks/usePdfDownload';
import { formatDuration, formatCost, formatDateTime } from '@/lib/format';
import type { Analysis } from '@/types/analysis';

interface AnalysisResultProps {
  analysis: Analysis;
}

interface PdfDownloadButtonProps {
  analysisId: string;
}

function PdfDownloadButton({ analysisId }: PdfDownloadButtonProps) {
  const { download, isLoading, isError } = usePdfDownload(analysisId);

  return (
    <div className="flex flex-col gap-2">
      <Button
        variant="secondary"
        size="md"
        loading={isLoading}
        onClick={() => void download()}
        className="w-full sm:w-auto"
      >
        <span aria-hidden>↓</span>
        Descargar Copia Literal (PDF)
      </Button>
      {isError && (
        <p className="text-xs text-red-600">
          No se pudo generar el enlace de descarga. Intenta de nuevo.
        </p>
      )}
    </div>
  );
}

export default function AnalysisResult({ analysis }: AnalysisResultProps) {
  const cargasVigentes = analysis.cargas_encontradas.filter((c) => c.vigente);
  const cargasCanceladas = analysis.cargas_encontradas.filter((c) => !c.vigente);

  const hasPdf = Boolean(analysis.pdf_storage_path);

  return (
    <div className="flex flex-col gap-6">
      {/* Summary header */}
      <Card padding="md">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex flex-col gap-1">
            <h2 className="text-lg font-semibold text-slate-900">
              Partida {analysis.partida}
            </h2>
            <p className="text-sm text-slate-500">{analysis.oficina}</p>
            {analysis.completed_at && (
              <p className="text-xs text-slate-400">
                Completado el {formatDateTime(analysis.completed_at)}
              </p>
            )}
          </div>

          <div className="flex flex-wrap gap-4 sm:text-right">
            {analysis.duration_seconds != null && (
              <div>
                <p className="text-xs text-slate-400">Duracion</p>
                <p className="text-sm font-semibold text-slate-700">
                  {formatDuration(analysis.duration_seconds)}
                </p>
              </div>
            )}
            {analysis.total_asientos != null && (
              <div>
                <p className="text-xs text-slate-400">Asientos</p>
                <p className="text-sm font-semibold text-slate-700">
                  {analysis.total_asientos}
                </p>
              </div>
            )}
            {analysis.claude_cost_usd != null && (
              <div>
                <p className="text-xs text-slate-400">Costo</p>
                <p className="text-sm font-semibold text-slate-700">
                  {formatCost(analysis.claude_cost_usd)}
                </p>
              </div>
            )}
          </div>
        </div>

        {hasPdf && (
          <div className="mt-4 border-t border-slate-100 pt-4">
            <PdfDownloadButton analysisId={analysis.id} />
          </div>
        )}
      </Card>

      {/* Informe */}
      {analysis.informe && (
        <Card padding="md">
          <h3 className="mb-3 text-sm font-semibold text-slate-900">Informe</h3>
          <p className="text-sm leading-relaxed text-slate-600 whitespace-pre-wrap">
            {analysis.informe}
          </p>
        </Card>
      )}

      {/* Cargas */}
      <Card padding="md">
        <div className="mb-4 flex items-center justify-between gap-2">
          <h3 className="text-sm font-semibold text-slate-900">Cargas y Gravamenes</h3>
          <div className="flex gap-2 text-xs">
            {cargasVigentes.length > 0 && (
              <span className="rounded-full bg-red-100 px-2 py-0.5 font-medium text-red-700">
                {cargasVigentes.length} vigente{cargasVigentes.length !== 1 ? 's' : ''}
              </span>
            )}
            {cargasCanceladas.length > 0 && (
              <span className="rounded-full bg-green-100 px-2 py-0.5 font-medium text-green-700">
                {cargasCanceladas.length} cancelada{cargasCanceladas.length !== 1 ? 's' : ''}
              </span>
            )}
            {analysis.cargas_encontradas.length === 0 && (
              <span className="rounded-full bg-slate-100 px-2 py-0.5 font-medium text-slate-600">
                Sin cargas
              </span>
            )}
          </div>
        </div>
        <CargasList cargas={analysis.cargas_encontradas} />
      </Card>

      {/* No PDF notice */}
      {!hasPdf && (
        <Alert variant="warning">
          El PDF de la copia literal no esta disponible para este analisis.
        </Alert>
      )}
    </div>
  );
}
