import { api } from './api';
import { AREA_REGISTRAL_DEFAULT } from '@/lib/constants';
import type {
  Analysis,
  AnalysisSummary,
  CreateAnalysisRequest,
  CreateAnalysisResponse,
  Pagination,
} from '@/types/analysis';
import type { AnalysisStatus } from '@/types/analysis';

interface ApiResponse<T> {
  data: T;
  error: null | { message: string; code?: string };
}

interface ListAnalysesParams {
  page?: number;
  per_page?: number;
  status?: AnalysisStatus;
}

interface ListAnalysesResponse {
  data: AnalysisSummary[];
  pagination: Pagination;
  error: null;
}

export const analysisService = {
  async create(request: CreateAnalysisRequest): Promise<CreateAnalysisResponse> {
    const body = {
      area_registral: AREA_REGISTRAL_DEFAULT,
      ...request,
    };
    const response = await api.post<ApiResponse<CreateAnalysisResponse>>(
      '/api/sunarp/analyze',
      body,
    );
    return response.data.data;
  },

  async list(params: ListAnalysesParams = {}): Promise<ListAnalysesResponse> {
    const response = await api.get<ListAnalysesResponse>('/api/sunarp/analyses', {
      params,
    });
    return response.data;
  },

  async getById(id: string): Promise<Analysis> {
    const response = await api.get<ApiResponse<Analysis>>(
      `/api/sunarp/analyses/${id}`,
    );
    return response.data.data;
  },

  async cancel(id: string): Promise<Analysis> {
    const response = await api.post<ApiResponse<Analysis>>(
      `/api/sunarp/analyses/${id}/cancel`,
    );
    return response.data.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/api/sunarp/analyses/${id}`);
  },
};
