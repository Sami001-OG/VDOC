'use client';

import { Film, Clock, Layers, Search } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { cn } from '@/lib/utils';

interface Stat {
  label: string;
  value: string;
  icon: typeof Film;
  color: string;
}

interface StatsCardsProps {
  videosProcessed?: number;
  totalDuration?: string;
  totalScenes?: number;
  searches?: number;
  loading?: boolean;
}

const colorMap: Record<string, string> = {
  cyan: 'bg-accent-cyan/10 text-accent-cyan',
  violet: 'bg-accent-violet/10 text-accent-violet',
  green: 'bg-accent-green/10 text-accent-green',
  blue: 'bg-accent-blue/10 text-accent-blue',
};

export function StatsCards({
  videosProcessed = 0,
  totalDuration = '0h',
  totalScenes = 0,
  searches = 0,
  loading,
}: StatsCardsProps) {
  const stats: Stat[] = [
    { label: 'Videos Processed', value: String(videosProcessed), icon: Film, color: 'cyan' },
    { label: 'Total Duration', value: totalDuration, icon: Clock, color: 'violet' },
    { label: 'Scenes Detected', value: String(totalScenes), icon: Layers, color: 'green' },
    { label: 'Searches', value: String(searches), icon: Search, color: 'blue' },
  ];

  if (loading) {
    return (
      <div className="grid grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <div className="shimmer h-4 w-20 rounded mb-3" />
            <div className="shimmer h-7 w-16 rounded" />
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <Card key={stat.label}>
          <div className="flex items-start justify-between">
            <div className="stat">
              <span className="stat-value">{stat.value}</span>
              <span className="stat-label">{stat.label}</span>
            </div>
            <div className={cn('w-9 h-9 rounded-lg flex items-center justify-center', colorMap[stat.color])}>
              <stat.icon className="w-4 h-4" />
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
