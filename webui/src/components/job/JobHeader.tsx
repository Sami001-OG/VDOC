'use client';

import { ArrowLeft, Download, RefreshCw } from 'lucide-react';
import Link from 'next/link';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { cn, getStatusColor } from '@/lib/utils';
import { PipelineVisualizer } from '@/components/dashboard/PipelineVisualizer';
import type { JobStatus } from '@/lib/types';

interface JobHeaderProps {
  job: JobStatus;
}

export function JobHeader({ job }: JobHeaderProps) {
  const steps = [
    { id: 'load', label: 'Load', status: (job.status === 'completed' ? 'done' : 'running') as 'done' | 'running' },
    { id: 'process', label: 'Process', status: (job.status === 'completed' ? 'done' : job.status === 'failed' ? 'error' : 'running') as 'done' | 'running' | 'error' },
    { id: 'render', label: 'Render', status: (job.status === 'completed' ? 'done' : 'pending') as 'done' | 'pending' },
  ] as const;

  return (
    <div className="space-y-4">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm">
        <Link href="/" className="text-text-muted hover:text-text-primary transition-colors">
          Dashboard
        </Link>
        <span className="text-text-muted">/</span>
        <span className="text-text-secondary">{job.id}</span>
      </div>

      <Card>
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <Link href="/">
                <Button variant="ghost" size="sm" className="p-1">
                  <ArrowLeft className="w-4 h-4" />
                </Button>
              </Link>
              <h1 className="text-lg font-semibold text-text-primary">
                {job.video}
              </h1>
              <Badge color={getStatusColor(job.status)}>
                {job.status.replace('_', ' ')}
              </Badge>
            </div>
            <p className="text-xs text-text-muted">ID: {job.id}</p>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm" icon={<RefreshCw className="w-3.5 h-3.5" />}>
              Reprocess
            </Button>
            <Button variant="primary" size="sm" icon={<Download className="w-3.5 h-3.5" />}>
              Download
            </Button>
          </div>
        </div>

        {/* Pipeline Status */}
        <div className="mt-4 pt-4 border-t border-surface-200">
          <PipelineVisualizer steps={steps as any} compact />
        </div>
      </Card>
    </div>
  );
}
