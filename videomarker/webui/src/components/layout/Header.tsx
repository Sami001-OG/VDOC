'use client';

import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Bell, Terminal } from 'lucide-react';

const pageTitles: Record<string, string> = {
  '/': 'Dashboard',
  '/processors': 'Processors',
  '/docs': 'Documentation',
  '/settings': 'Settings',
};

export function Header() {
  const pathname = usePathname();
  const title = pageTitles[pathname] || 'Dashboard';

  const isJobPage = pathname.startsWith('/jobs/');

  return (
    <header className="sticky top-0 z-20 h-14 flex items-center justify-between px-6 bg-surface-50/80 backdrop-blur-sm border-b border-surface-200">
      <div className="flex items-center gap-3">
        {isJobPage ? (
          <span className="text-sm font-medium text-text-primary">
            Job Details
          </span>
        ) : (
          <span className="text-sm font-semibold text-text-primary">{title}</span>
        )}
      </div>

      <div className="flex items-center gap-2">
        <button className="btn-ghost p-2 rounded-lg" title="Toggle Logs">
          <Terminal className="w-4 h-4" />
        </button>
        <button className="btn-ghost p-2 rounded-lg relative" title="Notifications">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-accent-cyan" />
        </button>
      </div>
    </header>
  );
}
