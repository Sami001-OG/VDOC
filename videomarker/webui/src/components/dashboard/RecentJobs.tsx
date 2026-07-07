'use client';

import Link from 'next/link';
import { ExternalLink, Clock } from 'lucide-react';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { TableRowSkeleton } from '@/components/ui/Skeleton';
import { cn, formatTimestamp, getStatusColor } from '@/lib/utils';
import type { JobStatus } from '@/lib/types';

interface RecentJobsProps {
  jobs: JobStatus[];
  loading?: boolean;
}

export function RecentJobs({ jobs, loading }: RecentJobsProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Jobs</CardTitle>
        {jobs.length > 0 && (
          <span className="text-xs text-text-muted">{jobs.length} total</span>
        )}
      </CardHeader>

      {loading ? (
        <div className="space-y-1">
          {Array.from({ length: 4 }).map((_, i) => (
            <TableRowSkeleton key={i} cols={4} />
          ))}
        </div>
      ) : jobs.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <Clock className="w-8 h-8 text-surface-400 mb-2" />
          <p className="text-sm text-text-muted">No jobs yet</p>
          <p className="text-xs text-text-muted mt-1">
            Upload a video to get started
          </p>
        </div>
      ) : (
        <div className="divide-y divide-surface-200">
          {jobs.map((job) => (
            <Link
              key={job.id}
              href={`/jobs/${job.id}`}
              className="flex items-center gap-4 px-4 py-3 hover:bg-surface-150 transition-colors group"
            >
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-text-primary truncate">
                  {job.video}
                </p>
                <p className="text-xs text-text-muted mt-0.5">
                  {job.id}
                </p>
              </div>

              <Badge color={getStatusColor(job.status)}>
                {job.status.replace('_', ' ')}
              </Badge>

              <ExternalLink className="w-4 h-4 text-surface-400 group-hover:text-text-secondary transition-colors shrink-0" />
            </Link>
          ))}
        </div>
      )}
    </Card>
  );
}
