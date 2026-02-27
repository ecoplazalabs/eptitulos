import { useState, useEffect, type FormEvent } from 'react';
import { useNavigate } from 'react-router';
import { useAuth } from '@/hooks/useAuth';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Alert from '@/components/ui/Alert';

export default function LoginPage() {
  const navigate = useNavigate();
  const { user, isLoading, signIn } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Redirect if already authenticated
  useEffect(() => {
    if (!isLoading && user) {
      void navigate('/dashboard', { replace: true });
    }
  }, [user, isLoading, navigate]);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (submitting) return;

    setError(null);
    setSubmitting(true);

    try {
      await signIn(email.trim(), password);
      void navigate('/dashboard', { replace: true });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Error al iniciar sesion. Intenta de nuevo.';
      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  // Show nothing while checking session to avoid flash
  if (isLoading) return null;

  return (
    <div className="relative flex min-h-dvh flex-col items-center justify-center overflow-hidden bg-slate-50 px-4">
      {/* Subtle background gradient */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            'radial-gradient(ellipse 80% 60% at 50% -10%, rgba(14,165,233,0.10) 0%, transparent 70%)',
        }}
      />

      {/* Card */}
      <div className="relative z-10 w-full max-w-sm">
        {/* Logo / brand */}
        <div className="mb-8 flex flex-col items-center gap-3">
          <div className="flex size-12 items-center justify-center rounded-2xl bg-brand-600 shadow-lg shadow-brand-600/30">
            <span className="text-lg font-bold text-white tracking-tight">EP</span>
          </div>
          <div className="text-center">
            <h1 className="text-xl font-semibold text-slate-900 tracking-tight">
              EP Titulos
            </h1>
            <p className="mt-1 text-sm text-slate-500">
              Analista SUNARP Automatizado
            </p>
          </div>
        </div>

        {/* Form card */}
        <div className="rounded-2xl border border-slate-200 bg-white px-6 py-8 shadow-sm">
          {error && (
            <Alert variant="error" className="mb-5">
              {error}
            </Alert>
          )}

          <form onSubmit={(e) => void handleSubmit(e)} noValidate>
            <div className="flex flex-col gap-4">
              <Input
                id="email"
                type="email"
                label="Correo electronico"
                placeholder="tu@ecoplaza.pe"
                autoComplete="email"
                autoFocus
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={submitting}
              />

              <Input
                id="password"
                type="password"
                label="Contrasena"
                placeholder="••••••••"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={submitting}
              />

              <Button
                type="submit"
                variant="primary"
                size="lg"
                fullWidth
                loading={submitting}
                disabled={!email || !password}
                className="mt-2"
              >
                {submitting ? 'Iniciando sesion...' : 'Iniciar Sesion'}
              </Button>
            </div>
          </form>
        </div>

        {/* Footer note */}
        <p className="mt-6 text-center text-xs text-slate-400">
          Acceso restringido &middot; Solo personal EcoPlaza
        </p>
      </div>
    </div>
  );
}
