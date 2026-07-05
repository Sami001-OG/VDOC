'use client';

import Link from 'next/link';
import { MainLayout } from '@/components/layout/MainLayout';
import { Button } from '@/components/ui/Button';
import { FileQuestion } from 'lucide-react';

export default function NotFoundPage() {
  return (
    <MainLayout>
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
        <div className="w-14 h-14 rounded-xl bg-accent-amber/10 flex items-center justify-center mb-4">
          <FileQuestion className="w-6 h-6 text-accent-amber" />
        </div>
        <h1 className="text-xl font-semibold text-text-primary mb-2">
          Page not found
        </h1>
        <p className="text-sm text-text-muted mb-6">
          The page you&apos;re looking for doesn&apos;t exist or has been moved.
        </p>
        <Link href="/">
          <Button variant="primary">Back to Dashboard</Button>
        </Link>
      </div>
    </MainLayout>
  );
}
