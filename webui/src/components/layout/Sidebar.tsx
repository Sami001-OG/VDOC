'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  Film,
  Grid3X3,
  Settings,
  Server,
  BookOpen,
  type LucideIcon,
} from 'lucide-react';

interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
}

const navItems: NavItem[] = [
  { label: 'Dashboard', href: '/', icon: Grid3X3 },
  { label: 'Processors', href: '/processors', icon: Server },
  { label: 'Documentation', href: '/docs', icon: BookOpen },
  { label: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-full w-56 z-30 flex flex-col bg-surface-50 border-r border-surface-200">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-5 h-14 border-b border-surface-200">
        <div className="w-7 h-7 rounded-lg bg-accent-cyan/15 flex items-center justify-center">
          <Film className="w-4 h-4 text-accent-cyan" />
        </div>
        <div>
          <span className="text-sm font-semibold text-text-primary">VideoMarker</span>
          <span className="block text-[10px] text-text-muted font-medium tracking-wider uppercase">
            Studio
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-4 space-y-0.5">
        {navItems.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                active
                  ? 'bg-accent-cyan/10 text-accent-cyan'
                  : 'text-text-secondary hover:bg-surface-200 hover:text-text-primary'
              )}
            >
              <item.icon className="w-4 h-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-surface-200">
        <span className="text-[10px] text-text-muted">v0.1.0 · API connected</span>
      </div>
    </aside>
  );
}
