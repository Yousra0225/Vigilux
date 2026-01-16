'use client';

import React from 'react';
import { ExternalLink, Globe, Shield, Trash2, Edit } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface Competitor {
  id: string;
  name: string;
  url?: string;
  score: number;
  tracking_status: 'active' | 'archived';
}

interface CompetitorListProps {
  competitors: Competitor[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  loading: boolean;
}

export function CompetitorList({ competitors, selectedId, onSelect, loading }: CompetitorListProps) {
  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-16 bg-gray-100 dark:bg-gray-800 rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  if (competitors.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500 dark:text-gray-400">
        No competitors found.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {competitors.map((competitor) => (
        <div
          key={competitor.id}
          onClick={() => onSelect(competitor.id)}
          className={cn(
            "p-4 rounded-lg border cursor-pointer transition-colors flex items-center justify-between",
            selectedId === competitor.id
              ? "bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800"
              : "bg-white border-gray-100 hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-750"
          )}
        >
          <div className="flex items-center space-x-3">
            <div className={cn(
                "p-2 rounded-full",
                selectedId === competitor.id ? "bg-blue-100 dark:bg-blue-800" : "bg-gray-100 dark:bg-gray-700"
            )}>
              <Globe className={cn("w-5 h-5", selectedId === competitor.id ? "text-blue-600 dark:text-blue-300" : "text-gray-500 dark:text-gray-400")} />
            </div>
            <div>
              <h3 className="font-medium text-gray-900 dark:text-white">{competitor.name}</h3>
              {competitor.url && (
                <a 
                  href={competitor.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-xs text-gray-500 hover:text-blue-500 flex items-center gap-1 mt-0.5"
                  onClick={(e) => e.stopPropagation()}
                >
                    {new URL(competitor.url).hostname} <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="text-right">
               <span className={cn(
                   "text-sm font-bold px-2 py-1 rounded",
                   competitor.score > 70 ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" :
                   competitor.score > 40 ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400" :
                   "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
               )}>
                   {competitor.score}
               </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
