import { useAuth } from '@/hooks/useAuth';
import Button from '@/components/ui/Button';

interface HeaderProps {
  title?: string;
  onMenuToggle?: () => void;
  sidebarCollapsed?: boolean;
}

export default function Header({ title, onMenuToggle, sidebarCollapsed }: HeaderProps) {
  const { user, signOut } = useAuth();

  const handleSignOut = () => {
    void signOut();
  };

  return (
    <header className="flex h-14 shrink-0 items-center gap-4 border-b border-slate-200 bg-white px-4 md:px-6">
      {/* Mobile hamburger / collapse toggle */}
      <button
        type="button"
        onClick={onMenuToggle}
        aria-label={sidebarCollapsed ? 'Expandir sidebar' : 'Colapsar sidebar'}
        className="flex size-8 items-center justify-center rounded-lg text-slate-500 transition-colors duration-150 hover:bg-slate-100 hover:text-slate-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
      >
        <span className="text-base leading-none" aria-hidden="true">
          ☰
        </span>
      </button>

      {/* Page title */}
      {title && (
        <h1 className="text-sm font-semibold text-slate-900 truncate">
          {title}
        </h1>
      )}

      {/* Spacer */}
      <div className="flex-1" />

      {/* User info + logout */}
      <div className="flex items-center gap-3">
        {user?.email && (
          <span className="hidden text-xs text-slate-500 md:block truncate max-w-[200px]">
            {user.email}
          </span>
        )}
        <Button
          variant="ghost"
          size="sm"
          onClick={handleSignOut}
          aria-label="Cerrar sesion"
          className="text-slate-500 hover:text-red-600 hover:bg-red-50"
        >
          <span className="text-sm leading-none" aria-hidden="true">
            ↪
          </span>
          <span className="hidden sm:inline">Salir</span>
        </Button>
      </div>
    </header>
  );
}
