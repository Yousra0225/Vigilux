'use client';

import { Loader2 } from 'lucide-react';

interface TaskProgressProps {
  competitorName: string;
}

export function TaskProgress({ competitorName }: TaskProgressProps) {
  return (
    <div className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-8 text-center animate-in fade-in-50 duration-300">
      <div className="flex justify-center mb-4">
        <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
      </div>
      <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
        Scanning in Progress
      </h3>
      <p className="text-gray-500 dark:text-gray-400 mt-2">
        Our AI engines are currently scanning{' '}
        <span className="font-bold">{competitorName}</span> for new breakthroughs.
      </p>
      <p className="text-sm text-gray-500 mt-1">
        This section will update automatically when the scan is complete.
      </p>
    </div>
  );
}
