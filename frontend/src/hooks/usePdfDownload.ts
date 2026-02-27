import { useState, useCallback } from 'react';
import { TOKEN_KEY } from '@/services/api';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8000';

interface UsePdfDownloadResult {
  download: () => Promise<void>;
  isLoading: boolean;
  isError: boolean;
}

export function usePdfDownload(analysisId: string): UsePdfDownloadResult {
  const [isLoading, setIsLoading] = useState(false);
  const [isError, setIsError] = useState(false);

  const download = useCallback(async () => {
    setIsLoading(true);
    setIsError(false);

    try {
      const token = localStorage.getItem(TOKEN_KEY);
      const url = `${API_BASE_URL}/api/sunarp/analyses/${analysisId}/pdf`;

      const response = await fetch(url, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);

      const anchor = document.createElement('a');
      anchor.href = objectUrl;
      anchor.download = `partida-${analysisId}.pdf`;
      document.body.appendChild(anchor);
      anchor.click();
      document.body.removeChild(anchor);

      // Release the object URL after a short delay to allow the download to start
      setTimeout(() => URL.revokeObjectURL(objectUrl), 10_000);
    } catch {
      setIsError(true);
    } finally {
      setIsLoading(false);
    }
  }, [analysisId]);

  return { download, isLoading, isError };
}
