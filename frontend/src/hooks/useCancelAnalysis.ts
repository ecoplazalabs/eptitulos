import { useMutation, useQueryClient } from '@tanstack/react-query';
import { analysisService } from '@/services/analysis-service';

export function useCancelAnalysis(id: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => analysisService.cancel(id),
    onSuccess: (updated) => {
      queryClient.setQueryData(['analysis', id], updated);
      void queryClient.invalidateQueries({ queryKey: ['analyses'] });
    },
  });
}
