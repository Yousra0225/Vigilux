'use client';

import React from 'react';
import { ExternalLink, Globe, Shield, Trash2, Edit, RotateCw, Activity, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface Competitor {
  id: string;
  name: string;
  url?: string;
  score: number;
  status: 'ACTIVE' | 'ARCHIVED';
}

interface CompetitorListProps {
  competitors: Competitor[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  loading: boolean;
  onRefresh?: (id: string) => void;
  processingStates?: Record<string, string>;
}

export function CompetitorList({ 
  competitors, 
  selectedId, 
  onSelect, 
  loading,
  onRefresh,
  processingStates 
}: CompetitorListProps) {
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
      {competitors.map((competitor) => {
        const status = processingStates?.[competitor.id];
        const isProcessing = status === 'scraping_started' || status === 'analysis_started' || status === 'requested';
        const isComplete = status === 'analysis_complete';
        
        return (
          <div
            key={competitor.id}
            onClick={() => onSelect(competitor.id)}
            className={cn(
              "p-4 rounded-lg border cursor-pointer transition-colors flex flex-col gap-3",
              selectedId === competitor.id
                ? "bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800"
                : "bg-white border-gray-100 hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-750"
            )}
          >
            <div className="flex items-center justify-between w-full">
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
              
              <div className="flex items-center gap-3">
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
                {onRefresh && (
                  <button
                      onClick={(e) => {
                          e.stopPropagation();
                          onRefresh(competitor.id);
                      }}
                      disabled={isProcessing}
                      className={cn(
                          "p-2 rounded-full transition-colors",
                          isProcessing 
                            ? "text-blue-500 cursor-not-allowed bg-blue-50 dark:bg-blue-900/20" 
                            : "text-gray-400 hover:text-blue-500 hover:bg-gray-100 dark:hover:bg-gray-700"
                      )}
                      title="Refresh analysis"
                  >
                      <RotateCw className={cn("w-4 h-4", isProcessing && "animate-spin")} />
                  </button>
                )}
              </div>
            </div>

            {/* Progress / Status Section */}
            {(isProcessing || isComplete) && (
              <div className="w-full pl-12 pr-2">
                {isProcessing && (
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-xs font-medium text-blue-600 dark:text-blue-400">
                      <span className="animate-pulse">
                        {status === 'scraping_started' ? 'Scraping latest data...' : 
                         status === 'analysis_started' ? 'Analyzing market signals...' : 
                         'Starting update...'}
                      </span>
                    </div>
                    <div className="h-1 w-full bg-blue-100 dark:bg-blue-900/50 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-500 rounded-full w-2/3 animate-[pulse_1s_ease-in-out_infinite] origin-left"></div>
                    </div>
                  </div>
                )}
                
                {isComplete && (
                   <div className="text-xs text-green-600 dark:text-green-400 flex items-center gap-1.5 animate-in fade-in slide-in-from-top-1 duration-500">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span className="font-medium">Analysis just updated</span>
                   </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
