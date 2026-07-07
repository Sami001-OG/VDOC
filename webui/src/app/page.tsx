'use client';

import { useState, useCallback } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { UploadZone } from '@/components/dashboard/UploadZone';
import { StatsCards } from '@/components/dashboard/StatsCards';
import { RecentJobs } from '@/components/dashboard/RecentJobs';
import { PipelineVisualizer } from '@/components/dashboard/PipelineVisualizer';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import type { JobStatus } from '@/lib/types';

const pipelineSteps = [
  { id: 'provider', label: 'Load Video', status: 'done' as const },
  { id: 'frames', label: 'Extract Frames', status: 'done' as const },
  { id: 'audio', label: 'Extract Audio', status: 'done' as const },
  { id: 'scenes', label: 'Detect Scenes', status: 'done' as const },
  { id: 'transcript', label: 'Transcribe', status: 'done' as const },
  { id: 'ocr', label: 'OCR', status: 'done' as const },
  { id: 'vision', label: 'Vision Analysis', status: 'done' as const },
  { id: 'semantic', label: 'Semantic Analysis', status: 'done' as const },
  { id: 'render', label: 'Render Output', status: 'done' as const },
];

export default function DashboardPage() {
  const [jobs, setJobs] = useState<JobStatus[]>([]);

  const handleJobCreated = useCallback((job: JobStatus) => {
    setJobs((prev) => {
      const existing = prev.findIndex((j) => j.id === job.id);
      if (existing >= 0) {
        const updated = [...prev];
        updated[existing] = job;
        return updated;
      }
      return [job, ...prev];
    });
  }, []);

  return (
    <MainLayout>
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h2 className="text-xl font-semibold text-text-primary">
            Video Pipeline
          </h2>
          <p className="text-sm text-text-muted mt-1">
            Upload a video to generate a structured MarkDirectory
          </p>
        </div>

        {/* Upload Zone */}
        <UploadZone onJobCreated={handleJobCreated} />

        {/* Stats */}
        <StatsCards
          videosProcessed={jobs.filter((j) => j.status === 'completed').length}
          totalDuration="—"
          totalScenes={0}
          searches={0}
        />

        {/* Pipeline + Recent Jobs */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Pipeline Overview */}
          <Card>
            <CardHeader>
              <CardTitle>Pipeline Stages</CardTitle>
            </CardHeader>
            <PipelineVisualizer steps={pipelineSteps} />
          </Card>

          {/* Recent Jobs */}
          <div className="lg:col-span-2">
            <RecentJobs jobs={jobs} />
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
