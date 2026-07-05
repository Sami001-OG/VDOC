'use client';

import { useRef, useState, useEffect, useCallback } from 'react';
import { Play, Clock } from 'lucide-react';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { cn, formatTimestamp } from '@/lib/utils';
import type { Scene, Chapter } from '@/lib/types';

interface TimelineExplorerProps {
  scenes: Scene[];
  chapters?: Chapter[];
  duration: number;
  onSeek?: (timestamp: number) => void;
  activeScene?: number | null;
}

export function TimelineExplorer({
  scenes,
  chapters,
  duration,
  onSeek,
  activeScene,
}: TimelineExplorerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [hoverPos, setHoverPos] = useState<number | null>(null);

  const getLeft = useCallback(
    (time: number) => (time / duration) * 100,
    [duration]
  );

  const getWidth = useCallback(
    (start: number, end: number) => ((end - start) / duration) * 100,
    [duration]
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>Timeline</CardTitle>
        <span className="text-xs text-text-muted">
          {formatTimestamp(duration)} total
        </span>
      </CardHeader>

      {/* Timeline Bar */}
      <div
        ref={containerRef}
        className="relative h-16 bg-surface-200 rounded-lg overflow-hidden cursor-pointer"
        onMouseMove={(e) => {
          const rect = containerRef.current?.getBoundingClientRect();
          if (rect) setHoverPos(((e.clientX - rect.left) / rect.width) * duration);
        }}
        onMouseLeave={() => setHoverPos(null)}
        onClick={(e) => {
          const rect = containerRef.current?.getBoundingClientRect();
          if (rect && onSeek) {
            const rel = (e.clientX - rect.left) / rect.width;
            onSeek(rel * duration);
          }
        }}
      >
        {/* Chapter backgrounds */}
        {chapters?.map((ch) => (
          <div
            key={ch.id}
            className="absolute top-0 h-full bg-accent-violet/5 border-r border-accent-violet/10"
            style={{
              left: `${getLeft(ch.start_time)}%`,
              width: `${getWidth(ch.start_time, ch.end_time)}%`,
            }}
            title={ch.title}
          />
        ))}

        {/* Scene segments */}
        {scenes.map((scene) => (
          <div
            key={scene.id}
            className={cn(
              'absolute top-1 bottom-1 rounded-sm transition-colors cursor-pointer',
              activeScene === scene.number
                ? 'bg-accent-cyan/40 ring-1 ring-accent-cyan'
                : 'bg-accent-cyan/20 hover:bg-accent-cyan/30'
            )}
            style={{
              left: `${getLeft(scene.start_time)}%`,
              width: `${Math.max(getWidth(scene.start_time, scene.end_time), 0.3)}%`,
            }}
            title={`Scene ${scene.number}: ${formatTimestamp(scene.start_time)} - ${formatTimestamp(scene.end_time)}`}
          />
        ))}

        {/* Hover indicator */}
        {hoverPos !== null && (
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-text-primary/30 z-10"
            style={{ left: `${getLeft(hoverPos)}%` }}
          />
        )}
      </div>

      {/* Time labels */}
      <div className="flex items-center justify-between mt-2">
        <span className="text-[10px] text-text-muted">0:00</span>
        <span className="text-[10px] text-text-muted">
          {formatTimestamp(duration / 2)}
        </span>
        <span className="text-[10px] text-text-muted">{formatTimestamp(duration)}</span>
      </div>

      {/* Chapter list */}
      {chapters && chapters.length > 0 && (
        <div className="mt-3 space-y-1">
          {chapters.map((ch) => (
            <button
              key={ch.id}
              className="flex items-center gap-3 w-full px-3 py-2 rounded-lg hover:bg-surface-150 transition-colors text-left group"
              onClick={() => onSeek?.(ch.start_time)}
            >
              <Play className="w-3 h-3 text-surface-400 group-hover:text-accent-cyan transition-colors shrink-0" />
              <span className="text-xs font-medium text-text-primary flex-1 truncate">
                {ch.title}
              </span>
              <span className="text-[10px] text-text-muted shrink-0">
                {formatTimestamp(ch.start_time)}
              </span>
            </button>
          ))}
        </div>
      )}
    </Card>
  );
}
