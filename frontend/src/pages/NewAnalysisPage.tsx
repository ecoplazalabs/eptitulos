import { Link } from 'react-router';
import Card from '@/components/ui/Card';
import AnalysisForm from '@/components/analysis/AnalysisForm';

export default function NewAnalysisPage() {
  return (
    <div className="mx-auto flex max-w-lg flex-col gap-6">
      {/* Breadcrumb */}
      <nav aria-label="Breadcrumb">
        <ol className="flex items-center gap-1.5 text-sm text-slate-500">
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
          <li>
            <span className="text-slate-900">Nuevo Analisis</span>
          </li>
        </ol>
      </nav>

      {/* Page heading */}
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold text-slate-900">Nuevo Analisis</h1>
        <p className="text-sm text-slate-500">
          Solicita el analisis de una partida registral de SUNARP
        </p>
      </div>

      {/* Form card */}
      <Card padding="lg">
        <AnalysisForm />
      </Card>
    </div>
  );
}
