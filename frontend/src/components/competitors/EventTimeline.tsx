'use client';

import React from 'react';
import { AlertTriangle, TrendingUp, DollarSign, Activity, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface Event {
  id: string;
  competitor_id: string;
  event_type: 'price' | 'feature' | 'health' | 'new_entrant';
  description: string;
  score: number;
  timestamp: string;
}

interface EventTimelineProps {
  events: Event[];
  loading: boolean;
}

const getEventIcon = (type: string) => {
  switch (type) {
    case 'price': return DollarSign;
    case 'feature': return Zap;
    case 'health': return Activity;
    case 'new_entrant': return AlertTriangle;
    default: return TrendingUp;
  }
};

const getEventColor = (type: string, score: number) => {
    if (score > 7) return "text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/30";
    switch (type) {
        case 'price': return "text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/30";
        case 'feature': return "text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/30";
        case 'health': return "text-purple-600 bg-purple-100 dark:text-purple-400 dark:bg-purple-900/30";
        default: return "text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-800";
    }
};

export function EventTimeline({ events, loading }: EventTimelineProps) {
  if (loading) {
     return (
        <div className="space-y-6">
            {[1, 2, 3].map(i => (
                <div key={i} className="flex gap-4">
                    <div className="w-2 bg-gray-200 dark:bg-gray-700 rounded-full h-full min-h-[50px] animate-pulse"></div>
                    <div className="flex-1 space-y-2">
                        <div className="h-4 w-1/4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
                        <div className="h-10 bg-gray-100 dark:bg-gray-800 rounded animate-pulse"></div>
                    </div>
                </div>
            ))}
        </div>
     );
  }

  if (events.length === 0) {
      return <div className="text-gray-500 dark:text-gray-400 italic">No recent activity detected.</div>;
  }

  return (
    <div className="relative border-l-2 border-gray-200 dark:border-gray-700 ml-3 space-y-8 pb-4">
      {events.map((event) => {
        const Icon = getEventIcon(event.event_type);
        const isBreakthrough = event.score > 7;

        return (
          <div key={event.id} className="relative pl-8">
            <span className={cn(
                "absolute -left-[11px] top-1 flex h-6 w-6 items-center justify-center rounded-full ring-4 ring-white dark:ring-gray-900",
                isBreakthrough ? "bg-red-500 text-white" : "bg-gray-200 dark:bg-gray-700 text-gray-500"
            )}>
              {isBreakthrough ? <AlertTriangle className="h-3 w-3" /> : <div className="h-2 w-2 rounded-full bg-gray-400" />}
            </span>
            
            <div className={cn(
                "p-4 rounded-lg border",
                isBreakthrough 
                  ? "bg-red-50 border-red-100 dark:bg-red-900/10 dark:border-red-900/50" 
                  : "bg-white border-gray-100 dark:bg-gray-800 dark:border-gray-700"
            )}>
                <div className="flex justify-between items-start mb-1">
                    <div className="flex items-center gap-2">
                        <span className={cn("p-1 rounded text-xs font-semibold uppercase", getEventColor(event.event_type, event.score))}>
                            {event.event_type}
                        </span>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                             {new Date(event.timestamp).toLocaleDateString()}
                        </span>
                    </div>
                    {isBreakthrough && (
                        <span className="text-xs font-bold text-red-600 dark:text-red-400 flex items-center gap-1">
                            Breakthrough <AlertTriangle className="w-3 h-3" />
                        </span>
                    )}
                </div>
                <p className="text-gray-800 dark:text-gray-200 text-sm leading-relaxed">
                    {event.description}
                </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
