import { useMutation, useQueryClient } from '@tanstack/react-query';
import { analysisService } from '@/services/analysis-service';
import type { CreateAnalysisRequest } from '@/types/analysis';

export function useCreateAnalysis() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CreateAnalysisRequest) =>
      analysisService.create(request),
    onSuccess: () => {
      // Invalidate the analyses list so it refetches
      void queryClient.invalidateQueries({ queryKey: ['analyses'] });
    },
  });
}
