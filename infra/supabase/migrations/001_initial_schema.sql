-- =============================================================
-- EP Titulos - Schema Completo
-- Ejecutar en Supabase SQL Editor
-- =============================================================

-- Tabla de analisis SUNARP
CREATE TABLE IF NOT EXISTS sunarp_analyses (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requested_by       UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    oficina            TEXT NOT NULL,
    partida            TEXT NOT NULL,
    area_registral     TEXT NOT NULL DEFAULT 'Propiedad Inmueble Predial',
    status             TEXT NOT NULL DEFAULT 'pending'
                       CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    total_asientos     INTEGER,
    pdf_storage_path   TEXT,
    informe            TEXT,
    cargas_encontradas JSONB NOT NULL DEFAULT '[]'::jsonb,
    error_message      TEXT,
    started_at         TIMESTAMPTZ,
    completed_at       TIMESTAMPTZ,
    duration_seconds   INTEGER,
    claude_cost_usd    DECIMAL(6,4),
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE sunarp_analyses IS 'Registra cada solicitud de analisis de partida SUNARP';
COMMENT ON COLUMN sunarp_analyses.pdf_storage_path IS 'Path en Supabase Storage (bucket sunarp-documents)';
COMMENT ON COLUMN sunarp_analyses.cargas_encontradas IS 'Array JSON: [{tipo, detalle, vigente, fecha}]';
COMMENT ON COLUMN sunarp_analyses.claude_cost_usd IS 'Costo de la API de Anthropic para esta ejecucion';

-- Trigger para updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON sunarp_analyses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================
-- Indices
-- =============================================================

-- Indice por usuario (para historial)
CREATE INDEX idx_analyses_requested_by ON sunarp_analyses(requested_by);

-- Indice por status (para queries de analisis activos)
CREATE INDEX idx_analyses_status ON sunarp_analyses(status)
    WHERE status IN ('pending', 'processing');

-- Indice por fecha de creacion (para ordenar historial)
CREATE INDEX idx_analyses_created_at ON sunarp_analyses(created_at DESC);

-- Indice compuesto para buscar duplicados
CREATE INDEX idx_analyses_oficina_partida ON sunarp_analyses(oficina, partida);

-- =============================================================
-- Row Level Security (RLS)
-- =============================================================

ALTER TABLE sunarp_analyses ENABLE ROW LEVEL SECURITY;

-- Usuarios solo ven sus propios analisis
CREATE POLICY "Users can view own analyses"
    ON sunarp_analyses
    FOR SELECT
    USING (auth.uid() = requested_by);

-- Usuarios pueden crear analisis (se asigna su ID)
CREATE POLICY "Users can create own analyses"
    ON sunarp_analyses
    FOR INSERT
    WITH CHECK (auth.uid() = requested_by);

-- service_role bypasea RLS automaticamente (para n8n y backend)

-- =============================================================
-- Supabase Storage - Bucket para PDFs
-- =============================================================

INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'sunarp-documents',
    'sunarp-documents',
    false,
    52428800,  -- 50MB max
    ARRAY['application/pdf']
);

-- RLS para Storage: usuarios solo ven sus propios PDFs
CREATE POLICY "Users can read own PDFs"
    ON storage.objects
    FOR SELECT
    USING (
        bucket_id = 'sunarp-documents'
        AND (storage.foldername(name))[1] = auth.uid()::text
    );
