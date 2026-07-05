'use client';

import { useMemo, useRef, useEffect } from 'react';
import { MessageSquare } from 'lucide-react';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { cn, formatTimestamp } from '@/lib/utils';

interface TranscriptSegment {
  start: number;
  end: number;
  text: string;
  speaker_id?: string;
}

interface TranscriptPanelProps {
  segments: TranscriptSegment[];
  activeTimestamp?: number;
  onSeek?: (timestamp: number) => void;
}

export function TranscriptPanel({
  segments,
  activeTimestamp,
  onSeek,
}: TranscriptPanelProps) {
  const activeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    activeRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }, [activeTimestamp]);

  if (segments.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Transcript</CardTitle>
        </CardHeader>
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <MessageSquare className="w-8 h-8 text-surface-400 mb-2" />
          <p className="text-sm text-text-muted">No transcript available</p>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Transcript</CardTitle>
        <span className="text-xs text-text-muted">{segments.length} segments</span>
      </CardHeader>
      <div className="max-h-[500px] overflow-y-auto space-y-1">
        {segments.map((seg, i) => {
          const isActive =
            activeTimestamp !== undefined &&
            seg.start <= activeTimestamp &&
            seg.end >= activeTimestamp;

          return (
            <button
              key={i}
              ref={isActive ? activeRef : undefined}
              onClick={() => onSeek?.(seg.start)}
              className={cn(
                'w-full text-left px-4 py-2 rounded-lg transition-all duration-200',
                isActive
                  ? 'bg-accent-cyan/10 border-l-2 border-accent-cyan'
                  : 'hover:bg-surface-150 border-l-2 border-transparent'
              )}
            >
              <div className="flex items-start gap-3">
                <span className="text-[10px] text-text-muted font-mono mt-0.5 shrink-0 w-14">
                  {formatTimestamp(seg.start)}
                </span>
                <div className="min-w-0">
                  {seg.speaker_id && (
                    <span className="text-[10px] font-medium text-accent-violet uppercase tracking-wider">
                      {seg.speaker_id}
                    </span>
                  )}
                  <p className="text-sm text-text-primary mt-0.5">{seg.text}</p>
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </Card>
  );
}
