'use client';

import { useState } from 'react';
import { ImageIcon } from 'lucide-react';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { cn, formatTimestamp } from '@/lib/utils';
import type { Scene } from '@/lib/types';

interface SceneGridProps {
  scenes: Scene[];
  onSelect?: (scene: Scene) => void;
  activeScene?: number | null;
}

export function SceneGrid({ scenes, onSelect, activeScene }: SceneGridProps) {
  const [imageErrors, setImageErrors] = useState<Set<number>>(new Set());

  if (scenes.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Scenes</CardTitle>
        </CardHeader>
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <ImageIcon className="w-8 h-8 text-surface-400 mb-2" />
          <p className="text-sm text-text-muted">No scenes detected</p>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Scenes</CardTitle>
        <span className="text-xs text-text-muted">{scenes.length} total</span>
      </CardHeader>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
        {scenes.map((scene) => (
          <button
            key={scene.id}
            onClick={() => onSelect?.(scene)}
            className={cn(
              'group relative rounded-lg overflow-hidden border transition-all duration-200',
              activeScene === scene.number
                ? 'border-accent-cyan ring-1 ring-accent-cyan/30'
                : 'border-surface-200 hover:border-surface-400'
            )}
          >
            {/* Thumbnail */}
            <div className="aspect-video bg-surface-200 flex items-center justify-center">
              {imageErrors.has(scene.number) ? (
                <ImageIcon className="w-6 h-6 text-surface-400" />
              ) : (
                <img
                  src={`/api/scene/${encodeURIComponent(scene.id)}/${scene.number}/thumbnail`}
                  alt={`Scene ${scene.number}`}
                  className="w-full h-full object-cover"
                  onError={() =>
                    setImageErrors((prev) => new Set(prev).add(scene.number))
                  }
                />
              )}
            </div>

            {/* Info overlay */}
            <div className="p-2">
              <p className="text-xs font-medium text-text-primary truncate">
                Scene {scene.number}
              </p>
              <div className="flex items-center justify-between mt-1">
                <span className="text-[10px] text-text-muted">
                  {formatTimestamp(scene.start_time)}
                </span>
                <span className="text-[10px] text-text-muted">
                  {formatTimestamp(scene.end_time)}
                </span>
              </div>
              {scene.description && (
                <p className="text-[10px] text-text-muted mt-1 line-clamp-2">
                  {scene.description}
                </p>
              )}
            </div>
          </button>
        ))}
      </div>
    </Card>
  );
}
