import { formatDistanceToNow, format } from 'date-fns';
import { es } from 'date-fns/locale';

/**
 * Format a date string to a human-readable relative time.
 * Example: "hace 3 minutos"
 */
export function formatRelativeTime(dateString: string): string {
  return formatDistanceToNow(new Date(dateString), {
    addSuffix: true,
    locale: es,
  });
}

/**
 * Format a date string to a full localized datetime.
 * Example: "25 feb. 2026, 10:30"
 */
export function formatDateTime(dateString: string): string {
  return format(new Date(dateString), "d MMM yyyy, HH:mm", { locale: es });
}

/**
 * Format a date string to a short date.
 * Example: "25/02/2026"
 */
export function formatDate(dateString: string): string {
  return format(new Date(dateString), 'dd/MM/yyyy');
}

/**
 * Format duration in seconds to a human-readable string.
 * Example: 263 -> "4m 23s"
 */
export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  if (remainingSeconds === 0) return `${minutes}m`;
  return `${minutes}m ${remainingSeconds}s`;
}

/**
 * Format a USD cost to a readable string.
 * Example: 4.25 -> "$4.25"
 */
export function formatCost(usd: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  }).format(usd);
}
