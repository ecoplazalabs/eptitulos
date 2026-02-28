import { useMutation, useQueryClient } from '@tanstack/react-query';
import { analysisService } from '@/services/analysis-service';

export function useDeleteAnalysis(id: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => analysisService.delete(id),
    onSuccess: () => {
      queryClient.removeQueries({ queryKey: ['analysis', id] });
      void queryClient.invalidateQueries({ queryKey: ['analyses'] });
    },
  });
}
