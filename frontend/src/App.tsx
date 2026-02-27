import { lazy, Suspense } from 'react';
import type { ReactNode } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router';
import { useAuth } from '@/hooks/useAuth';
import Spinner from '@/components/ui/Spinner';

const LoginPage = lazy(() => import('@/pages/LoginPage'));
const DashboardPage = lazy(() => import('@/pages/DashboardPage'));
const NewAnalysisPage = lazy(() => import('@/pages/NewAnalysisPage'));
const AnalysisDetailPage = lazy(() => import('@/pages/AnalysisDetailPage'));
const AppLayout = lazy(() => import('@/components/layout/AppLayout'));

function PageLoader() {
  return (
    <div className="flex min-h-dvh items-center justify-center">
      <Spinner size="lg" />
    </div>
  );
}

interface AuthGuardProps {
  children: ReactNode;
}

function AuthGuard({ children }: AuthGuardProps) {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <PageLoader />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function ProtectedLayout() {
  return (
    <AuthGuard>
      <AppLayout>
        <Outlet />
      </AppLayout>
    </AuthGuard>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route element={<ProtectedLayout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/analyses/new" element={<NewAnalysisPage />} />
            <Route path="/analyses/:id" element={<AnalysisDetailPage />} />
          </Route>

          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
