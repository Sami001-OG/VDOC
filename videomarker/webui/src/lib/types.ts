export interface JobStatus {
  id: string;
  status: 'queued' | 'running' | 'completed' | 'completed_with_errors' | 'failed';
  video: string;
  video_path: string;
  output_path: string;
  errors?: Record<string, string>;
  error?: string;
}

export interface Scene {
  id: string;
  number: number;
  start_time: number;
  end_time: number;
  start_timestamp: string;
  end_timestamp: string;
  description: string | null;
}

export interface Chapter {
  id: string;
  number: number;
  title: string;
  start_time: number;
  end_time: number;
  start_timestamp: string;
  end_timestamp: string;
  scene_ids: string[];
}

export interface Timeline {
  duration: number;
  scenes: Scene[];
  chapters: Chapter[];
}

export interface SceneDetail {
  scene_number: number;
  files: Record<string, string>;
  metadata?: {
    scene_number: number;
    start_time: number;
    end_time: number;
    start_timestamp: string;
    end_timestamp: string;
    duration: number;
    description: string | null;
    type: string;
  };
}

export interface ProcessorInfo {
  name: string;
  dependencies: string[];
  priority: number;
}

export interface SearchResult {
  id: string;
  text: string;
  score: number;
  source_type: string;
  timestamp: number;
  scene_number?: number;
  chapter_title?: string;
  preview?: string;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
}

export interface VideoMetadata {
  file: string;
  file_size: number;
  duration: number;
  fps: number;
  resolution: { width: number; height: number };
  codec: string;
  format: string;
  has_audio: boolean;
  total_frames: number;
}
