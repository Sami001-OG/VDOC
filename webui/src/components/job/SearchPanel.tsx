'use client';

import { useState, useCallback } from 'react';
import { Search, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { cn, formatTimestamp, formatConfidence } from '@/lib/utils';
import * as api from '@/lib/api';
import type { SearchResult } from '@/lib/types';

interface SearchPanelProps {
  jobId: string;
  onSeek?: (timestamp: number) => void;
}

export function SearchPanel({ jobId, onSeek }: SearchPanelProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = useCallback(async () => {
    if (!query.trim()) return;
    setLoading(true);
    setSearched(true);
    try {
      const res = await api.searchVideo(jobId, query);
      setResults(res);
    } catch {
      setResults([]);
    }
    setLoading(false);
  }, [query, jobId]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Semantic Search</CardTitle>
      </CardHeader>

      {/* Search Input */}
      <div className="relative mb-4">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          placeholder="Search transcript, OCR, captions…"
          className="input-base pl-10 pr-10"
        />
        {loading && (
          <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-accent-cyan animate-spin-slow" />
        )}
      </div>

      {/* Results */}
      {searched && results.length === 0 && !loading && (
        <div className="flex flex-col items-center justify-center py-6 text-center">
          <Search className="w-6 h-6 text-surface-400 mb-2" />
          <p className="text-sm text-text-muted">No results found</p>
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-2 max-h-[400px] overflow-y-auto">
          {results.map((result) => (
            <button
              key={result.id}
              onClick={() => onSeek?.(result.timestamp)}
              className="w-full text-left px-4 py-3 rounded-lg hover:bg-surface-150 transition-colors border border-transparent hover:border-surface-200"
            >
              <div className="flex items-start gap-3">
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-text-primary line-clamp-2">{result.text}</p>
                  <div className="flex items-center gap-2 mt-1.5">
                    <Badge color="cyan" className="text-[10px]">
                      {result.source_type}
                    </Badge>
                    <span className="text-[10px] text-text-muted">
                      {formatTimestamp(result.timestamp)}
                    </span>
                    <span className="text-[10px] text-text-muted">
                      {formatConfidence(result.score)}
                    </span>
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}
    </Card>
  );
}
