'use client';

import { FileText } from 'lucide-react';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';

interface OCRViewerProps {
  content?: string | null;
  sceneNumber?: number;
}

export function OCRViewer({ content, sceneNumber }: OCRViewerProps) {
  if (!content) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>OCR Text</CardTitle>
        </CardHeader>
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <FileText className="w-8 h-8 text-surface-400 mb-2" />
          <p className="text-sm text-text-muted">No OCR data available</p>
          <p className="text-xs text-text-muted mt-1">
            Select a scene with detected text
          </p>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>OCR Text</CardTitle>
        {sceneNumber && (
          <span className="text-xs text-text-muted">Scene {sceneNumber}</span>
        )}
      </CardHeader>
      <div className="max-h-[400px] overflow-y-auto">
        <pre className="text-sm text-text-secondary font-mono whitespace-pre-wrap px-4 py-3">
          {content}
        </pre>
      </div>
    </Card>
  );
}
