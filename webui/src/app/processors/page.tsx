'use client';

import { useEffect, useState } from 'react';
import { Server, Cpu, ArrowRight, Hash } from 'lucide-react';
import { MainLayout } from '@/components/layout/MainLayout';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { CardSkeleton } from '@/components/ui/Skeleton';
import * as api from '@/lib/api';
import type { ProcessorInfo } from '@/lib/types';

export default function ProcessorsPage() {
  const [processors, setProcessors] = useState<ProcessorInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getProcessors()
      .then(setProcessors)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <h2 className="text-xl font-semibold text-text-primary">Processors</h2>
          <p className="text-sm text-text-muted mt-1">
            Available plugins in the processing pipeline
          </p>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        ) : processors.length === 0 ? (
          <Card>
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Server className="w-10 h-10 text-surface-400 mb-3" />
              <p className="text-sm text-text-muted">No processors found</p>
              <p className="text-xs text-text-muted mt-1">
                Ensure the API server is running
              </p>
            </div>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {processors.map((p) => (
              <Card key={p.name} hover>
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-md bg-accent-violet/10 flex items-center justify-center">
                      <Cpu className="w-3.5 h-3.5 text-accent-violet" />
                    </div>
                    <CardTitle>{p.name}</CardTitle>
                  </div>
                  <Badge color="violet">v0.1</Badge>
                </CardHeader>

                <div className="space-y-2">
                  {p.dependencies.length > 0 && (
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-text-muted">Deps:</span>
                      {p.dependencies.map((dep) => (
                        <Badge key={dep} color="default" className="text-[10px]">
                          {dep}
                        </Badge>
                      ))}
                    </div>
                  )}
                  <div className="flex items-center gap-2">
                    <Hash className="w-3 h-3 text-text-muted" />
                    <span className="text-xs text-text-muted">
                      Priority: {p.priority}
                    </span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </MainLayout>
  );
}
