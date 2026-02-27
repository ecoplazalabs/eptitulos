import { useState, useCallback, useEffect } from 'react';
import type { ReactNode } from 'react';
import { useLocation } from 'react-router';
import { cn } from '@/lib/cn';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';

interface AppLayoutProps {
  children: ReactNode;
}

const PAGE_TITLES: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/analyses/new': 'Nuevo Analisis',
};

function resolveTitle(pathname: string): string {
  if (PAGE_TITLES[pathname]) return PAGE_TITLES[pathname];
  if (pathname.startsWith('/analyses/')) return 'Detalle del Analisis';
  return 'EP Titulos';
}

export default function AppLayout({ children }: AppLayoutProps) {
  const { pathname } = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [desktopCollapsed, setDesktopCollapsed] = useState(false);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  const toggleMenu = useCallback(() => {
    // On mobile (< md) toggle the overlay; on desktop toggle collapse
    if (window.innerWidth < 768) {
      setMobileOpen((prev) => !prev);
    } else {
      setDesktopCollapsed((prev) => !prev);
    }
  }, []);

  const title = resolveTitle(pathname);

  return (
    <div className="flex min-h-dvh bg-slate-50">
      {/* Desktop Sidebar */}
      <div className="hidden md:flex md:flex-col md:shrink-0">
        <div className="sticky top-0 h-dvh">
          <Sidebar collapsed={desktopCollapsed} />
        </div>
      </div>

      {/* Mobile sidebar overlay */}
      {mobileOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-30 bg-slate-900/40 backdrop-blur-sm md:hidden"
            aria-hidden="true"
            onClick={() => setMobileOpen(false)}
          />
          {/* Drawer */}
          <div className="fixed inset-y-0 left-0 z-40 flex flex-col md:hidden">
            <Sidebar collapsed={false} />
          </div>
        </>
      )}

      {/* Main content */}
      <div className="flex min-w-0 flex-1 flex-col">
        <Header
          title={title}
          onMenuToggle={toggleMenu}
          sidebarCollapsed={desktopCollapsed}
        />

        <main
          className={cn(
            'flex-1 px-4 py-6 md:px-8 md:py-8',
            'max-w-6xl w-full mx-auto',
          )}
        >
          {children}
        </main>
      </div>
    </div>
  );
}
