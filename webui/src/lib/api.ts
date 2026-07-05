import type { JobStatus, Timeline, SceneDetail, ProcessorInfo, SearchResult } from './types';

const BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => 'Unknown error');
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
}

export async function processVideo(
  file: File,
  config?: string,
  onProgress?: (percent: number) => void
): Promise<JobStatus> {
  const form = new FormData();
  form.append('file', file);
  if (config) form.append('config', config);

  // Use XMLHttpRequest for upload progress
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', `${BASE}/process`);

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    };

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        reject(new Error(`Upload failed: ${xhr.status}`));
      }
    };

    xhr.onerror = () => reject(new Error('Upload failed'));
    xhr.send(form);
  });
}

export async function getJobStatus(jobId: string): Promise<JobStatus> {
  return request<JobStatus>(`/status/${jobId}`);
}

export async function getTimeline(jobId: string): Promise<Timeline> {
  return request<Timeline>(`/timeline/${jobId}`);
}

export async function getSummary(jobId: string): Promise<string> {
  const res = await fetch(`${BASE}/summary/${jobId}`);
  if (!res.ok) throw new Error(`Failed to get summary: ${res.status}`);
  return res.text();
}

export async function getScene(
  jobId: string,
  sceneNumber: number
): Promise<SceneDetail> {
  return request<SceneDetail>(`/scene/${jobId}/${sceneNumber}`);
}

export async function searchVideo(
  jobId: string,
  query: string,
  topK = 10
): Promise<SearchResult[]> {
  const form = new FormData();
  form.append('job_id', jobId);
  form.append('query', query);
  form.append('top_k', String(topK));

  const res = await fetch(`${BASE}/search`, { method: 'POST', body: form });
  if (!res.ok) throw new Error(`Search failed: ${res.status}`);
  return res.json();
}

export async function getProcessors(): Promise<ProcessorInfo[]> {
  return request<ProcessorInfo[]>('/processors');
}

export async function getDownloadUrl(jobId: string): Promise<string> {
  const res = await fetch(`${BASE}/download/${jobId}`);
  if (!res.ok) throw new Error(`Download failed: ${res.status}`);
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}

export function pollJobStatus(
  jobId: string,
  onUpdate: (status: JobStatus) => void,
  interval = 1500
): () => void {
  let cancelled = false;
  let retries = 0;

  async function poll() {
    while (!cancelled) {
      try {
        const status = await getJobStatus(jobId);
        onUpdate(status);
        if (
          status.status === 'completed' ||
          status.status === 'completed_with_errors' ||
          status.status === 'failed'
        ) {
          return;
        }
        retries = 0;
      } catch {
        retries++;
        if (retries > 10) return;
      }
      await new Promise((r) => setTimeout(r, interval));
    }
  }

  poll();
  return () => { cancelled = true; };
}
