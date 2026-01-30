'use client';

import React from 'react';
import { X, Globe, TrendingUp, AlertCircle, CheckCircle2, DollarSign, BarChart3 } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface CompetitorDetail {
  id: string;
  name: string;
  url?: string;
  score: number;
  pitch: string;
  estimated_revenue: string;
  strengths: string[];
  weaknesses: string[];
  market_sentiment: string;
  status: 'ACTIVE' | 'ARCHIVED';
}

interface QuickViewModalProps {
  competitor: CompetitorDetail | null;
  isOpen: boolean;
  onClose: () => void;
  loading: boolean;
}

export function QuickViewModal({ competitor, isOpen, onClose, loading }: QuickViewModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className="bg-white dark:bg-gray-900 w-full max-w-2xl rounded-xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh] animate-in zoom-in-95 duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-6 border-b border-gray-100 dark:border-gray-800 flex justify-between items-center bg-gray-50/50 dark:bg-gray-800/50">
          <div className="flex items-center gap-4">
             <div className="w-12 h-12 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-xl">
                {competitor?.name.charAt(0)}
             </div>
             <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">{competitor?.name || 'Loading...'}</h2>
                {competitor?.url && (
                    <a href={competitor.url} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:underline flex items-center gap-1">
                        <Globe className="w-3 h-3" /> {new URL(competitor.url).hostname}
                    </a>
                )}
             </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-200 dark:hover:bg-gray-800 rounded-full transition-colors text-gray-500">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-8">
          {loading ? (
             <div className="space-y-6">
                <div className="h-4 bg-gray-100 dark:bg-gray-800 rounded w-3/4 animate-pulse" />
                <div className="grid grid-cols-2 gap-4">
                    <div className="h-20 bg-gray-100 dark:bg-gray-800 rounded animate-pulse" />
                    <div className="h-20 bg-gray-100 dark:bg-gray-800 rounded animate-pulse" />
                </div>
                <div className="h-32 bg-gray-100 dark:bg-gray-800 rounded animate-pulse" />
             </div>
          ) : competitor && (
            <>
              {/* Pitch */}
              <section>
                <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">AI Pitch</h3>
                <p className="text-gray-700 dark:text-gray-200 leading-relaxed italic border-l-4 border-blue-500 pl-4 py-1 bg-blue-50/30 dark:bg-blue-900/10">
                  "{competitor.pitch}"
                </p>
              </section>

              {/* Stats Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="p-4 rounded-lg bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 text-center">
                    <TrendingUp className="w-5 h-5 text-blue-600 dark:text-blue-400 mx-auto mb-2" />
                    <p className="text-xs text-gray-500 dark:text-gray-400">Threat Score</p>
                    <p className="text-xl font-bold text-gray-900 dark:text-white">{competitor.score}/100</p>
                </div>
                <div className="p-4 rounded-lg bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 text-center">
                    <DollarSign className="w-5 h-5 text-green-600 dark:text-green-400 mx-auto mb-2" />
                    <p className="text-xs text-gray-500 dark:text-gray-400">Est. Revenue</p>
                    <p className="text-xl font-bold text-gray-900 dark:text-white">{competitor.estimated_revenue}</p>
                </div>
                <div className="p-4 rounded-lg bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 text-center">
                    <BarChart3 className="w-5 h-5 text-purple-600 dark:text-purple-400 mx-auto mb-2" />
                    <p className="text-xs text-gray-500 dark:text-gray-400">Sentiment</p>
                    <p className="text-xl font-bold text-gray-900 dark:text-white">{competitor.market_sentiment}</p>
                </div>
              </div>

              {/* Strengths & Weaknesses */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                   <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                       <CheckCircle2 className="w-4 h-4 text-green-500" /> Strengths
                   </h3>
                   <ul className="space-y-2">
                      {competitor.strengths.map((s, i) => (
                        <li key={i} className="text-sm text-gray-700 dark:text-gray-200 bg-green-50/50 dark:bg-green-900/10 px-3 py-2 rounded-md border border-green-100/50 dark:border-green-900/30">
                           {s}
                        </li>
                      ))}
                   </ul>
                </div>
                <div>
                   <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                       <AlertCircle className="w-4 h-4 text-red-500" /> Weaknesses
                   </h3>
                   <ul className="space-y-2">
                      {competitor.weaknesses.map((w, i) => (
                        <li key={i} className="text-sm text-gray-700 dark:text-gray-200 bg-red-50/50 dark:bg-red-900/10 px-3 py-2 rounded-md border border-red-100/50 dark:border-red-900/30">
                           {w}
                        </li>
                      ))}
                   </ul>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-800/50 flex justify-end">
            <button 
                onClick={onClose}
                className="px-6 py-2 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-lg font-medium hover:opacity-90 transition-opacity"
            >
                Close
            </button>
        </div>
      </div>
    </div>
  );
}
