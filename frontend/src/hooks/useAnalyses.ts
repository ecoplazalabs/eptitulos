import { useQuery } from '@tanstack/react-query';
import { analysisService } from '@/services/analysis-service';
import { ANALYSES_PER_PAGE } from '@/lib/constants';
import type { AnalysisStatus } from '@/types/analysis';

interface UseAnalysesParams {
  page?: number;
  perPage?: number;
  status?: AnalysisStatus;
}

export function useAnalyses(params: UseAnalysesParams = {}) {
  const { page = 1, perPage = ANALYSES_PER_PAGE, status } = params;

  return useQuery({
    queryKey: ['analyses', { page, perPage, status }],
    queryFn: () =>
      analysisService.list({
        page,
        per_page: perPage,
        status,
      }),
  });
}
