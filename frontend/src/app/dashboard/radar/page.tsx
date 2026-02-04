'use client';

import React, { useState, useEffect } from 'react';
import { Search, Plus, Lock, Globe, ExternalLink, ShieldAlert, Loader2, BarChart2 } from 'lucide-react';
import api from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import { CompetitorRadarChart } from '@/components/radar/CompetitorRadarChart';

interface RadarCompetitor {
  name: string;
  url: string;
  threat_score: number;
  pitch: string;
  strengths: string[];
  weaknesses: string[];
}

interface Project {
  id: string;
  name: string;
}

export default function RadarPage() {
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<RadarCompetitor[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [isAdding, setIsAdding] = useState<string | null>(null);
  const [selectedCompetitor, setSelectedCompetitor] = useState<RadarCompetitor | null>(null);

  const isStarter = user?.plan_type === 'starter';

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const res = await api.get<Project[]>('/api/v1/projects/');
        setProjects(res.data);
      } catch (error) {
        console.error('Error fetching projects:', error);
      }
    };
    fetchProjects();
  }, []);

  const generateRadarData = (comp: RadarCompetitor) => {
    // Synthetic mapping based on threat_score
    const score = comp.threat_score;
    return [
      { subject: 'Market Presence', A: score, fullMark: 100 },
      { subject: 'Innovation', A: Math.min(100, Math.round(score * 1.1)), fullMark: 100 },
      { subject: 'Pricing Power', A: Math.min(100, Math.round(100 - (score * 0.4))), fullMark: 100 },
      { subject: 'Customer Sentiment', A: Math.min(100, Math.round(score * 0.9 + 5)), fullMark: 100 },
      { subject: 'Growth Velocity', A: Math.min(100, Math.round(score * 0.95)), fullMark: 100 },
    ];
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.length < 3) {
      toast.error('Search query must be at least 3 characters');
      return;
    }
    setIsSearching(true);
    setSelectedCompetitor(null);
    try {
      const response = await api.get<RadarCompetitor[]>('/api/v1/competitors/radar', {
        params: { query: searchQuery }
      });
      setResults(response.data);
      if (response.data.length > 0) {
        // Default to the highest threat
        const topThreat = response.data.reduce((prev, current) => 
          (prev.threat_score > current.threat_score) ? prev : current
        );
        setSelectedCompetitor(topThreat);
      }
      toast.success(`Found ${response.data.length} potential competitors`);
    } catch (error) {
      console.error('Radar search failed:', error);
      toast.error('Failed to scan market');
    } finally {
      setIsSearching(false);
    }
  };

  const handleAddCompetitor = async (competitor: RadarCompetitor) => {
    if (projects.length === 0) {
      toast.error('No project found. Please create a project first.');
      return;
    }

    setIsAdding(competitor.name);
    try {
      await api.post('/api/v1/competitors/', {
        name: competitor.name,
        url: competitor.url,
        project_id: projects[0].id, // Default to first project
      });
      toast.success(`${competitor.name} added to dashboard`);
    } catch (error: any) {
      console.error('Error adding competitor:', error);
      const detail = error.response?.data?.detail || 'Failed to add competitor';
      toast.error(detail);
    } finally {
      setIsAdding(null);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Global Radar</h1>
          <p className="text-gray-500 dark:text-gray-400">Discover potential competitors and market threats using AI.</p>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-900 p-6 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm">
        <form onSubmit={handleSearch} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 h-5 w-5" />
            <input
              type="text"
              placeholder="Search by industry, keyword, or domain..."
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 focus:ring-2 focus:ring-blue-500 outline-none"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <button
            type="submit"
            disabled={isSearching}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 flex items-center gap-2"
          >
            {isSearching ? <Loader2 className="animate-spin h-5 w-5" /> : <Search className="h-5 w-5" />}
            Scan Market
          </button>
        </form>
      </div>

      {selectedCompetitor && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="lg:col-span-1">
             <CompetitorRadarChart 
                data={generateRadarData(selectedCompetitor)} 
                color={selectedCompetitor.threat_score > 70 ? '#ef4444' : selectedCompetitor.threat_score > 40 ? '#f59e0b' : '#10b981'}
             />
          </div>
          <div className="lg:col-span-2 bg-white dark:bg-gray-900 p-6 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <BarChart2 className="h-5 w-5 text-blue-600" />
              Analysis: {selectedCompetitor.name}
            </h2>
            <div className="space-y-4">
               <div>
                  <h4 className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-1">Market Pitch</h4>
                  <p className="text-gray-900 dark:text-gray-100">{selectedCompetitor.pitch}</p>
               </div>
               <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <h4 className="text-sm font-semibold text-green-600 dark:text-green-400 mb-2">Key Strengths</h4>
                    <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-300 space-y-1">
                      {selectedCompetitor.strengths.slice(0, 4).map((s, i) => (
                        <li key={i}>{s}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-red-600 dark:text-red-400 mb-2">Key Weaknesses</h4>
                    <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-300 space-y-1">
                      {selectedCompetitor.weaknesses.slice(0, 4).map((w, i) => (
                        <li key={i}>{w}</li>
                      ))}
                    </ul>
                  </div>
               </div>
            </div>
          </div>
        </div>
      )}

      {results.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {results.map((competitor) => (
            <div
              key={competitor.name}
              onClick={() => setSelectedCompetitor(competitor)}
              className={cn(
                "group relative bg-white dark:bg-gray-900 rounded-xl border shadow-sm hover:shadow-md transition-all overflow-hidden cursor-pointer",
                selectedCompetitor?.name === competitor.name 
                  ? "border-blue-500 ring-1 ring-blue-500 dark:border-blue-400" 
                  : "border-gray-200 dark:border-gray-800"
              )}
            >
              {/* Threat Score Badge */}
              <div className="absolute top-4 right-4 z-10">
                <div className={cn(
                  "px-2 py-1 rounded text-xs font-bold",
                  competitor.threat_score > 70 ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" :
                  competitor.threat_score > 40 ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400" :
                  "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                )}>
                  Score: {competitor.threat_score}
                </div>
              </div>

              <div className="p-6">
                <div className="flex items-start gap-4 mb-4">
                  <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <Globe className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div>
                    <h3 className="font-bold text-lg text-gray-900 dark:text-white group-hover:text-blue-600 transition-colors">
                      {competitor.name}
                    </h3>
                    <p className="text-sm text-gray-500 truncate max-w-[150px]">
                      {competitor.url}
                    </p>
                  </div>
                </div>

                {/* Insights Section */}
                <div className="space-y-3 mb-6">
                  <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300">
                    <ShieldAlert className="h-4 w-4" />
                    AI Insights
                  </div>
                  
                  <div className={cn("space-y-2 transition-all", isStarter && "blur-[3px] select-none pointer-events-none")}>
                    <p className="text-xs text-gray-600 dark:text-gray-400 italic mb-2">
                      "{competitor.pitch}"
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {competitor.strengths?.map((strength: string, i: number) => (
                        <span key={i} className="text-[10px] bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400 px-2 py-0.5 rounded-full border border-green-100 dark:border-green-800">
                          {strength}
                        </span>
                      ))}
                      {competitor.weaknesses?.map((weakness: string, i: number) => (
                        <span key={i} className="text-[10px] bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400 px-2 py-0.5 rounded-full border border-red-100 dark:border-red-800">
                          {weakness}
                        </span>
                      ))}
                    </div>
                  </div>

                  {isStarter && (
                    <div className="absolute inset-0 bg-white/40 dark:bg-black/40 flex flex-col items-center justify-center p-6 text-center backdrop-blur-[1px] z-20 mt-24">
                       <Lock className="h-8 w-8 text-gray-600 dark:text-gray-300 mb-2" />
                       <p className="text-sm font-bold text-gray-900 dark:text-white">Growth Plan Required</p>
                       <p className="text-xs text-gray-600 dark:text-gray-400">Upgrade to reveal full AI analysis and threat signals.</p>
                       <button className="mt-4 text-xs bg-gray-900 dark:bg-white text-white dark:text-black px-4 py-2 rounded-full font-bold">
                         Upgrade Now
                       </button>
                    </div>
                  )}
                </div>

                <div className="pt-4 border-t border-gray-100 dark:border-gray-800 flex justify-between items-center">
                  <a
                    href={competitor.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-600 hover:underline flex items-center gap-1"
                  >
                    Visit Site <ExternalLink className="h-3 w-3" />
                  </a>
                  
                  <button
                    onClick={() => handleAddCompetitor(competitor)}
                    disabled={isAdding === competitor.name}
                    className="bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-900 dark:text-white px-3 py-1.5 rounded-md text-xs font-semibold transition-colors flex items-center gap-1"
                  >
                    {isAdding === competitor.name ? <Loader2 className="animate-spin h-3 w-3" /> : <Plus className="h-3 w-3" />}
                    Add to Dashboard
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {!isSearching && results.length === 0 && (
        <div className="text-center py-20 bg-gray-50 dark:bg-gray-900/50 rounded-xl border-2 border-dashed border-gray-200 dark:border-gray-800">
          <div className="max-w-md mx-auto">
            <div className="bg-blue-100 dark:bg-blue-900/30 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="h-8 w-8 text-blue-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Ready to Scan?</h3>
            <p className="text-gray-500 dark:text-gray-400">
              Enter a keyword or industry above to find hidden competitors and emerging market threats.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
