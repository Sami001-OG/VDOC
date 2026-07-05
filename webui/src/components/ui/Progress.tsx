'use client';

import { cn } from '@/lib/utils';

interface ProgressProps {
  value: number;
  className?: string;
  size?: 'sm' | 'md';
  label?: string;
}

export function Progress({ value, className, size = 'md', label }: ProgressProps) {
  const clamped = Math.min(100, Math.max(0, value));

  return (
    <div className={cn('flex flex-col gap-1', className)}>
      {label && (
        <div className="flex items-center justify-between">
          <span className="text-xs text-text-muted">{label}</span>
          <span className="text-xs font-medium text-text-secondary">{clamped}%</span>
        </div>
      )}
      <div
        className={cn(
          'w-full bg-surface-200 rounded-full overflow-hidden',
          size === 'sm' ? 'h-1' : 'h-2'
        )}
      >
        <div
          className="h-full rounded-full bg-accent-cyan transition-all duration-500 ease-out"
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
}
