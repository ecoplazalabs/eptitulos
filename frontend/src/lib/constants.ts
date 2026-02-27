export const OFICINAS_REGISTRALES = [
  { value: 'LIMA', label: 'Lima' },
  { value: 'AREQUIPA', label: 'Arequipa' },
  { value: 'TRUJILLO', label: 'Trujillo' },
  { value: 'CHICLAYO', label: 'Chiclayo' },
  { value: 'CUSCO', label: 'Cusco' },
  { value: 'HUANCAYO', label: 'Huancayo' },
  { value: 'PIURA', label: 'Piura' },
  { value: 'IQUITOS', label: 'Iquitos' },
  { value: 'TACNA', label: 'Tacna' },
  { value: 'ICA', label: 'Ica' },
  { value: 'PUNO', label: 'Puno' },
  { value: 'CAJAMARCA', label: 'Cajamarca' },
  { value: 'HUARAZ', label: 'Huaraz' },
  { value: 'CHIMBOTE', label: 'Chimbote' },
  { value: 'MOYOBAMBA', label: 'Moyobamba' },
] as const;

export type OficinaValue = (typeof OFICINAS_REGISTRALES)[number]['value'];

export const AREA_REGISTRAL_DEFAULT = 'Propiedad Inmueble Predial';

export const STATUS_LABELS = {
  pending: 'Pendiente',
  processing: 'Procesando',
  completed: 'Completado',
  failed: 'Fallido',
} as const;

export const POLLING_INTERVAL_MS = 5_000;

export const PDF_SIGNED_URL_EXPIRY_SECONDS = 3_600;

export const ANALYSES_PER_PAGE = 20;
