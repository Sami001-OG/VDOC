'use client';

import { useState, useCallback } from 'react';
import { useParams } from 'next/navigation';
import { MainLayout } from '@/components/layout/MainLayout';
import { JobHeader } from '@/components/job/JobHeader';
import { SceneGrid } from '@/components/job/SceneGrid';
import { TimelineExplorer } from '@/components/job/TimelineExplorer';
import { TranscriptPanel } from '@/components/job/TranscriptPanel';
import { ChapterViewer } from '@/components/job/ChapterViewer';
import { OCRViewer } from '@/components/job/OCRViewer';
import { SearchPanel } from '@/components/job/SearchPanel';
import { CardSkeleton } from '@/components/ui/Skeleton';
import { useJob, useScene } from '@/hooks/useJob';
import type { Scene } from '@/lib/types';

export default function JobDetailPage() {
  const params = useParams();
  const jobId = params.id as string;
  const { job, timeline, summary, loading } = useJob(jobId);
  const [activeScene, setActiveScene] = useState<number | null>(null);
  const [activeTimestamp, setActiveTimestamp] = useState<number | undefined>();

  const { scene: sceneDetail } = useScene(
    jobId,
    activeScene ?? undefined
  );

  const handleSceneSelect = useCallback(
    (scene: Scene) => {
      setActiveScene(scene.number);
      setActiveTimestamp(scene.start_time);
    },
    []
  );

  const handleSeek = useCallback((timestamp: number) => {
    setActiveTimestamp(timestamp);
    if (timeline) {
      const scene = timeline.scenes.find(
        (s) => s.start_time <= timestamp && s.end_time >= timestamp
      );
      if (scene) setActiveScene(scene.number);
    }
  }, [timeline]);

  if (loading || !job) {
    return (
      <MainLayout>
        <div className="max-w-6xl mx-auto space-y-4">
          <CardSkeleton />
          <CardSkeleton />
          <div className="grid grid-cols-2 gap-4">
            <CardSkeleton />
            <CardSkeleton />
          </div>
        </div>
      </MainLayout>
    );
  }

  const transcriptSegments = job.status === 'completed'
    ? timeline?.scenes.map((s) => ({
        start: s.start_time,
        end: s.end_time,
        text: s.description || `Scene ${s.number}`,
      })) ?? []
    : [];

  return (
    <MainLayout>
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Job Header */}
        <JobHeader job={job} />

        {/* Timeline */}
        {timeline && (
          <TimelineExplorer
            scenes={timeline.scenes}
            chapters={timeline.chapters}
            duration={timeline.duration}
            onSeek={handleSeek}
            activeScene={activeScene}
          />
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Scenes + Chapters */}
          <div className="lg:col-span-2 space-y-6">
            {/* Scene Grid */}
            {timeline && (
              <SceneGrid
                scenes={timeline.scenes}
                onSelect={handleSceneSelect}
                activeScene={activeScene}
              />
            )}

            {/* Summary */}
            {summary && (
              <div className="card p-4">
                <h3 className="text-sm font-semibold text-text-primary mb-3">
                  Summary
                </h3>
                <div className="prose-custom">{summary}</div>
              </div>
            )}

            {/* Transcript */}
            <TranscriptPanel
              segments={transcriptSegments}
              activeTimestamp={activeTimestamp}
              onSeek={handleSeek}
            />
          </div>

          {/* Right Column - Details + Search */}
          <div className="space-y-6">
            {/* Search */}
            <SearchPanel jobId={jobId} onSeek={handleSeek} />

            {/* Chapters */}
            {timeline && (
              <ChapterViewer
                chapters={timeline.chapters}
                onSeek={handleSeek}
                activeChapter={
                  timeline.chapters.find(
                    (ch) =>
                      activeTimestamp !== undefined &&
                      ch.start_time <= activeTimestamp &&
                      ch.end_time >= activeTimestamp
                  )?.number ?? null
                }
              />
            )}

            {/* OCR */}
            <OCRViewer
              content={sceneDetail?.files?.['ocr.md'] ?? null}
              sceneNumber={activeScene ?? undefined}
            />
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
