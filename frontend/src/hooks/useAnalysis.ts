import { useQuery } from '@tanstack/react-query';
import { analysisService } from '@/services/analysis-service';
import { POLLING_INTERVAL_MS } from '@/lib/constants';

export function useAnalysis(id: string) {
  return useQuery({
    queryKey: ['analysis', id],
    queryFn: () => analysisService.getById(id),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === 'pending' || status === 'processing') {
        return POLLING_INTERVAL_MS;
      }
      return false;
    },
  });
}
