import { NavLink } from 'react-router';
import { cn } from '@/lib/cn';

interface NavItem {
  to: string;
  label: string;
  icon: string;
}

const NAV_ITEMS: NavItem[] = [
  { to: '/dashboard', label: 'Dashboard', icon: '◻' },
  { to: '/analyses/new', label: 'Nuevo Analisis', icon: '+' },
];

interface SidebarProps {
  collapsed?: boolean;
}

export default function Sidebar({ collapsed = false }: SidebarProps) {
  return (
    <aside
      className={cn(
        'flex h-full flex-col border-r border-slate-200 bg-white transition-all duration-200',
        collapsed ? 'w-16' : 'w-60',
      )}
    >
      {/* Logo */}
      <div
        className={cn(
          'flex items-center border-b border-slate-100 px-4',
          'h-14 shrink-0',
          collapsed ? 'justify-center' : 'gap-2.5',
        )}
      >
        <span
          className="flex size-7 shrink-0 items-center justify-center rounded-lg bg-brand-600 text-sm font-bold text-white"
          aria-hidden="true"
        >
          EP
        </span>
        {!collapsed && (
          <span className="text-sm font-semibold text-slate-900 tracking-tight">
            EP Titulos
          </span>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex flex-1 flex-col gap-1 p-2" aria-label="Navegacion principal">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            title={collapsed ? item.label : undefined}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium',
                'transition-colors duration-150',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500',
                collapsed && 'justify-center',
                isActive
                  ? 'bg-brand-50 text-brand-700'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900',
              )
            }
          >
            <span
              className={cn(
                'shrink-0 text-base leading-none',
                item.icon === '+' && 'text-lg font-light',
              )}
              aria-hidden="true"
            >
              {item.icon}
            </span>
            {!collapsed && (
              <span className="truncate">{item.label}</span>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer space */}
      <div className="h-4 shrink-0" />
    </aside>
  );
}
