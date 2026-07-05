'use client';

import { useState, useRef, useCallback, type DragEvent } from 'react';
import { Upload, FileVideo, X, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { cn, formatFileSize } from '@/lib/utils';
import { Button } from '@/components/ui/Button';
import { Progress } from '@/components/ui/Progress';
import * as api from '@/lib/api';
import type { JobStatus } from '@/lib/types';

type UploadState = 'idle' | 'dragging' | 'uploading' | 'processing' | 'done' | 'error';

interface UploadZoneProps {
  onJobCreated: (job: JobStatus) => void;
}

export function UploadZone({ onJobCreated }: UploadZoneProps) {
  const [state, setState] = useState<UploadState>('idle');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(async (f: File) => {
    if (!f.type.startsWith('video/') && !f.name.match(/\.(mp4|mkv|mov|avi|webm|flv|m4v)$/i)) {
      setError('Unsupported video format');
      setState('error');
      return;
    }

    setFile(f);
    setState('uploading');
    setProgress(0);
    setError(null);

    try {
      const job = await api.processVideo(f, undefined, setProgress);
      setState('processing');
      onJobCreated(job);

      api.pollJobStatus(job.id, (updated) => {
        if (updated.status === 'completed' || updated.status === 'completed_with_errors') {
          setState('done');
        } else if (updated.status === 'failed') {
          setState('error');
          setError(updated.error || 'Processing failed');
        }
      });
    } catch (e) {
      setState('error');
      setError(e instanceof Error ? e.message : 'Upload failed');
    }
  }, [onJobCreated]);

  const onDrop = useCallback(
    (e: DragEvent) => {
      e.preventDefault();
      setState('idle');
      const f = e.dataTransfer.files[0];
      if (f) handleFile(f);
    },
    [handleFile]
  );

  const onDragOver = useCallback((e: DragEvent) => {
    e.preventDefault();
    setState('dragging');
  }, []);

  const onDragLeave = useCallback(() => {
    setState('idle');
  }, []);

  const reset = useCallback(() => {
    setState('idle');
    setProgress(0);
    setError(null);
    setFile(null);
  }, []);

  const isActive = state === 'uploading' || state === 'processing';

  return (
    <div
      onDrop={onDrop}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onClick={() => !isActive && inputRef.current?.click()}
      className={cn(
        'relative rounded-xl border-2 border-dashed p-8 text-center cursor-pointer transition-all duration-300',
        state === 'dragging' && 'border-accent-cyan/50 bg-accent-cyan/5 scale-[1.02]',
        state === 'idle' && 'border-surface-300 hover:border-surface-400 bg-surface-100/50',
        isActive && 'border-accent-cyan/30 bg-surface-100 cursor-default',
        state === 'done' && 'border-accent-green/30 bg-accent-green/5',
        state === 'error' && 'border-accent-red/30 bg-accent-red/5'
      )}
    >
      <input
        ref={inputRef}
        type="file"
        accept="video/mp4,video/mkv,video/mov,video/avi,video/webm,video/flv,video/m4v,.mp4,.mkv,.mov,.avi,.webm,.flv,.m4v"
        className="hidden"
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) handleFile(f);
        }}
      />

      {/* Idle State */}
      {state === 'idle' && (
        <div className="space-y-3 animate-fade-in">
          <div className="w-12 h-12 mx-auto rounded-xl bg-accent-cyan/10 flex items-center justify-center">
            <Upload className="w-5 h-5 text-accent-cyan" />
          </div>
          <div>
            <p className="text-sm font-medium text-text-primary">
              Drop video here or click to browse
            </p>
            <p className="text-xs text-text-muted mt-1">
              MP4, MKV, MOV, AVI, WEBM, FLV, M4V — up to 4GB
            </p>
          </div>
        </div>
      )}

      {/* Dragging State */}
      {state === 'dragging' && (
        <div className="space-y-2 animate-fade-in">
          <FileVideo className="w-8 h-8 mx-auto text-accent-cyan" />
          <p className="text-sm font-medium text-accent-cyan">Drop to process</p>
        </div>
      )}

      {/* Uploading State */}
      {state === 'uploading' && file && (
        <div className="space-y-3 animate-fade-in text-left max-w-sm mx-auto">
          <div className="flex items-center gap-3">
            <Loader2 className="w-5 h-5 text-accent-cyan animate-spin-slow shrink-0" />
            <div className="min-w-0">
              <p className="text-sm font-medium text-text-primary truncate">{file.name}</p>
              <p className="text-xs text-text-muted">{formatFileSize(file.size)}</p>
            </div>
          </div>
          <Progress value={progress} size="sm" />
        </div>
      )}

      {/* Processing State */}
      {state === 'processing' && (
        <div className="space-y-3 animate-fade-in">
          <Loader2 className="w-8 h-8 mx-auto text-accent-cyan animate-spin-slow" />
          <div>
            <p className="text-sm font-medium text-text-primary">Processing video…</p>
            <p className="text-xs text-text-muted mt-1">
              Extracting frames, transcribing, analyzing scenes
            </p>
          </div>
        </div>
      )}

      {/* Done State */}
      {state === 'done' && (
        <div className="space-y-2 animate-fade-in">
          <CheckCircle2 className="w-8 h-8 mx-auto text-accent-green" />
          <p className="text-sm font-medium text-accent-green">Processing complete</p>
          <Button variant="ghost" size="sm" onClick={reset}>
            Process another
          </Button>
        </div>
      )}

      {/* Error State */}
      {state === 'error' && (
        <div className="space-y-2 animate-fade-in">
          <AlertCircle className="w-8 h-8 mx-auto text-accent-red" />
          <p className="text-sm font-medium text-accent-red">{error || 'Upload failed'}</p>
          <Button variant="ghost" size="sm" onClick={reset}>
            Try again
          </Button>
        </div>
      )}
    </div>
  );
}
