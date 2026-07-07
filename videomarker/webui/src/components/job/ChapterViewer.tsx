'use client';

import { BookOpen, Play } from 'lucide-react';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { formatTimestamp } from '@/lib/utils';
import type { Chapter } from '@/lib/types';

interface ChapterViewerProps {
  chapters: Chapter[];
  onSeek?: (timestamp: number) => void;
  activeChapter?: number | null;
}

export function ChapterViewer({ chapters, onSeek, activeChapter }: ChapterViewerProps) {
  if (chapters.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Chapters</CardTitle>
        </CardHeader>
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <BookOpen className="w-8 h-8 text-surface-400 mb-2" />
          <p className="text-sm text-text-muted">No chapters detected</p>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Chapters</CardTitle>
        <span className="text-xs text-text-muted">{chapters.length} total</span>
      </CardHeader>
      <div className="space-y-1">
        {chapters.map((ch) => (
          <button
            key={ch.id}
            onClick={() => onSeek?.(ch.start_time)}
            className={`w-full text-left px-4 py-3 rounded-lg transition-all duration-200 ${
              activeChapter === ch.number
                ? 'bg-accent-violet/10 border-l-2 border-accent-violet'
                : 'hover:bg-surface-150 border-l-2 border-transparent'
            }`}
          >
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 rounded-md bg-accent-violet/10 flex items-center justify-center shrink-0">
                <Play className="w-3 h-3 text-accent-violet" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-text-primary truncate">
                  {ch.title}
                </p>
                <p className="text-xs text-text-muted mt-0.5">
                  {formatTimestamp(ch.start_time)} – {formatTimestamp(ch.end_time)}
                </p>
              </div>
              <span className="text-[10px] text-text-muted font-mono">
                {ch.scene_ids.length} scenes
              </span>
            </div>
          </button>
        ))}
      </div>
    </Card>
  );
}
