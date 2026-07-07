'use client';

import { cn } from '@/lib/utils';
import { CheckCircle2, Circle, Loader2, ArrowRight } from 'lucide-react';

interface Step {
  id: string;
  label: string;
  status: 'pending' | 'running' | 'done' | 'error';
}

interface PipelineVisualizerProps {
  steps?: Step[];
  compact?: boolean;
}

const defaultSteps: Step[] = [
  { id: 'provider', label: 'Load Video', status: 'pending' },
  { id: 'frames', label: 'Extract Frames', status: 'pending' },
  { id: 'audio', label: 'Extract Audio', status: 'pending' },
  { id: 'scenes', label: 'Detect Scenes', status: 'pending' },
  { id: 'transcript', label: 'Transcribe', status: 'pending' },
  { id: 'ocr', label: 'OCR', status: 'pending' },
  { id: 'vision', label: 'Vision Analysis', status: 'pending' },
  { id: 'semantic', label: 'Semantic Analysis', status: 'pending' },
  { id: 'render', label: 'Render Output', status: 'pending' },
];

const statusIcon = (status: Step['status']) => {
  switch (status) {
    case 'done':
      return <CheckCircle2 className="w-4 h-4 text-accent-green" />;
    case 'running':
      return <Loader2 className="w-4 h-4 text-accent-cyan animate-spin-slow" />;
    case 'error':
      return <CheckCircle2 className="w-4 h-4 text-accent-red" />;
    default:
      return <Circle className="w-4 h-4 text-surface-400" />;
  }
};

const statusColor = (status: Step['status']) => {
  switch (status) {
    case 'done':
      return 'text-accent-green';
    case 'running':
      return 'text-accent-cyan';
    case 'error':
      return 'text-accent-red';
    default:
      return 'text-text-muted';
  }
};

export function PipelineVisualizer({ steps = defaultSteps, compact }: PipelineVisualizerProps) {
  if (compact) {
    return (
      <div className="flex items-center gap-1.5">
        {steps.map((step, i) => (
          <div key={step.id} className="flex items-center gap-1.5">
            {statusIcon(step.status)}
            <span className={cn('text-xs font-medium', statusColor(step.status))}>
              {step.label}
            </span>
            {i < steps.length - 1 && (
              <ArrowRight className="w-3 h-3 text-surface-400" />
            )}
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {steps.map((step, i) => (
        <div key={step.id} className="flex items-center gap-3 py-1.5">
          <div className="w-5 flex justify-center">{statusIcon(step.status)}</div>
          <span className={cn('text-sm', statusColor(step.status))}>{step.label}</span>
          {i < steps.length - 1 && (
            <div className="w-px h-4 bg-surface-300 ml-2" />
          )}
        </div>
      ))}
    </div>
  );
}
