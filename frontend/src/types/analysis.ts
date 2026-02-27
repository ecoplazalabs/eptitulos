export type AnalysisStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface Carga {
  tipo: string;
  detalle: string;
  vigente: boolean;
  fecha: string | null;
}

export interface Analysis {
  id: string;
  requested_by: string;
  oficina: string;
  partida: string;
  area_registral: string;
  status: AnalysisStatus;
  total_asientos: number | null;
  pdf_storage_path: string | null;
  informe: string | null;
  cargas_encontradas: Carga[];
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  duration_seconds: number | null;
  claude_cost_usd: number | null;
  created_at: string;
  updated_at: string;
}

/** Lightweight version returned by the list endpoint */
export interface AnalysisSummary {
  id: string;
  oficina: string;
  partida: string;
  status: AnalysisStatus;
  total_asientos: number | null;
  cargas_count: number;
  duration_seconds: number | null;
  created_at: string;
  completed_at: string | null;
}

export interface CreateAnalysisRequest {
  oficina: string;
  partida: string;
  area_registral?: string;
}

export interface CreateAnalysisResponse {
  id: string;
  status: AnalysisStatus;
  oficina: string;
  partida: string;
  created_at: string;
}

export interface Pagination {
  page: number;
  per_page: number;
  total: number;
}
