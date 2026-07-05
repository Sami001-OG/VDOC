'use client';

import { useState, useEffect, useCallback } from 'react';
import type { JobStatus, Timeline, SceneDetail } from '@/lib/types';
import * as api from '@/lib/api';

export function useJob(jobId: string | undefined) {
  const [job, setJob] = useState<JobStatus | null>(null);
  const [timeline, setTimeline] = useState<Timeline | null>(null);
  const [summary, setSummary] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;

    setLoading(true);
    setError(null);

    const cancel = api.pollJobStatus(jobId, (status) => {
      setJob(status);
      setLoading(false);
    });

    return cancel;
  }, [jobId]);

  useEffect(() => {
    if (!jobId || job?.status !== 'completed') return;

    Promise.all([
      api.getTimeline(jobId).then(setTimeline).catch(() => {}),
      api.getSummary(jobId).then(setSummary).catch(() => {}),
    ]);
  }, [jobId, job?.status]);

  return { job, timeline, summary, loading, error };
}

export function useScene(
  jobId: string | undefined,
  sceneNumber: number | undefined
) {
  const [scene, setScene] = useState<SceneDetail | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!jobId || sceneNumber === undefined) return;

    setLoading(true);
    api
      .getScene(jobId, sceneNumber)
      .then(setScene)
      .catch(() => setScene(null))
      .finally(() => setLoading(false));
  }, [jobId, sceneNumber]);

  return { scene, loading };
}
