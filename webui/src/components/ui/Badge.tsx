'use client';

import type { HTMLAttributes, ReactNode } from 'react';
import { cn } from '@/lib/utils';

type BadgeColor = 'cyan' | 'blue' | 'violet' | 'green' | 'amber' | 'red' | 'default';

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  color?: BadgeColor;
  icon?: ReactNode;
}

const colorStyles: Record<BadgeColor, string> = {
  cyan: 'badge-cyan',
  blue: 'badge-blue',
  violet: 'badge-violet',
  green: 'badge-green',
  amber: 'badge-amber',
  red: 'badge-red',
  default: 'badge bg-surface-200 text-text-secondary border-surface-300',
};

export function Badge({ className, color = 'default', icon, children, ...props }: BadgeProps) {
  return (
    <span className={cn(colorStyles[color], className)} {...props}>
      {icon}
      {children}
    </span>
  );
}
