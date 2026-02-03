'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { Plus } from 'lucide-react';
import api from '@/lib/api';
import { toast } from 'sonner';
import { CompetitorList, Competitor } from '@/components/competitors/CompetitorList';
import { EventTimeline, Event } from '@/components/competitors/EventTimeline';
import { useWebSocket } from '@/hooks/use-socket';

interface Project {
    id: string;
    name: string;
}

export default function CompetitorsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [loadingCompetitors, setLoadingCompetitors] = useState(false);
  
  const [selectedCompetitorId, setSelectedCompetitorId] = useState<string | null>(null);
  const [events, setEvents] = useState<Event[]>([]);
  const [loadingEvents, setLoadingEvents] = useState(false);

  const [processingStates, setProcessingStates] = useState<Record<string, string>>({});
  const [refreshKey, setRefreshKey] = useState(0);
  const { lastMessage } = useWebSocket();

  const handleRefresh = useCallback(async (competitorId: string) => {
    try {
      setProcessingStates(prev => ({ ...prev, [competitorId]: 'requested' }));
      await api.post(`/api/v1/competitors/${competitorId}/refresh`);
      toast.success('Refresh requested');
    } catch (error) {
      console.error('Failed to refresh competitor', error);
      toast.error('Failed to start refresh');
      setProcessingStates(prev => {
          const newState = { ...prev };
          delete newState[competitorId];
          return newState;
      });
    }
  }, []);

  useEffect(() => {
    if (lastMessage?.type === 'TASK_UPDATE' && lastMessage.data) {
        const { competitor_id, status } = lastMessage.data;
        if (competitor_id) {
            setProcessingStates(prev => ({ ...prev, [competitor_id]: status }));
            
            if (status === 'analysis_complete') {
                 toast.success('Analysis updated');
                 setRefreshKey(prev => prev + 1);
                 
                 // Clear processing state after a delay
                 setTimeout(() => {
                     setProcessingStates(prev => {
                         const ns = { ...prev };
                         delete ns[competitor_id];
                         return ns;
                     });
                 }, 3000);
            } else if (String(status).includes('failed')) {
                toast.error('Analysis failed');
                setProcessingStates(prev => {
                     const ns = { ...prev };
                     delete ns[competitor_id];
                     return ns;
                 });
            }
        }
    }
  }, [lastMessage]);

  // 1. Fetch Projects on mount
  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const res = await api.get<Project[]>('/api/v1/projects/');
        setProjects(res.data);
        if (res.data.length > 0) {
            setSelectedProjectId(res.data[0].id);
        }
      } catch (error) {
        console.error('Failed to fetch projects', error);
        toast.error('Could not load projects');
      }
    };
    fetchProjects();
  }, []);

  // 2. Fetch Competitors when project changes
  useEffect(() => {
    if (!selectedProjectId) return;

    const fetchCompetitors = async () => {
      setLoadingCompetitors(true);
      try {
        const res = await api.get<Competitor[]>(`/api/v1/competitors/?project_id=${selectedProjectId}`);
        setCompetitors(res.data);
        if (res.data.length > 0) {
             // Auto-select first competitor to show timeline
             setSelectedCompetitorId(res.data[0].id);
        } else {
             setSelectedCompetitorId(null);
             setEvents([]);
        }
      } catch (error) {
        console.error('Failed to fetch competitors', error);
        toast.error('Could not load competitors');
      } finally {
        setLoadingCompetitors(false);
      }
    };
    fetchCompetitors();
  }, [selectedProjectId, refreshKey]);

  // 3. Fetch Events when competitor selected
  useEffect(() => {
    if (!selectedCompetitorId) return;

    const fetchEvents = async () => {
      setLoadingEvents(true);
      try {
        const res = await api.get<Event[]>(`/api/v1/competitors/${selectedCompetitorId}/events`);
        setEvents(res.data);
      } catch (error) {
        console.error('Failed to fetch events', error);
        toast.error('Could not load timeline');
      } finally {
        setLoadingEvents(false);
      }
    };
    fetchEvents();
  }, [selectedCompetitorId, refreshKey]);

  return (
    <div className="h-[calc(100vh-6rem)] flex flex-col">
      <div className="flex justify-between items-center mb-6">
         <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Competitors</h1>
            <p className="text-gray-500 dark:text-gray-400">Track and analyze your market competition</p>
         </div>
         {/* Placeholder for Add Competitor */}
         <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors opacity-50 cursor-not-allowed">
            <Plus className="w-4 h-4" />
            Add Competitor
         </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-full min-h-0">
        {/* List Section */}
        <div className="lg:col-span-5 flex flex-col bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-100 dark:border-gray-700 overflow-hidden">
            <div className="p-4 border-b border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 flex justify-between items-center">
               <h2 className="font-semibold text-gray-700 dark:text-gray-200">Tracked Entities</h2>
               {projects.length > 1 && (
                 <select 
                    value={selectedProjectId || ''} 
                    onChange={(e) => setSelectedProjectId(e.target.value)}
                    className="text-sm border rounded px-2 py-1 bg-white dark:bg-gray-700 border-gray-200 dark:border-gray-600"
                 >
                    {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                 </select>
               )}
            </div>
            <div className="flex-1 overflow-y-auto p-4">
                <CompetitorList 
                    competitors={competitors} 
                    selectedId={selectedCompetitorId}
                    onSelect={setSelectedCompetitorId}
                    loading={loadingCompetitors}
                    onRefresh={handleRefresh}
                    processingStates={processingStates}
                />
            </div>
        </div>

        {/* Timeline Section */}
        <div className="lg:col-span-7 flex flex-col bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-100 dark:border-gray-700 overflow-hidden">
             <div className="p-4 border-b border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 flex justify-between items-center">
               <h2 className="font-semibold text-gray-700 dark:text-gray-200">Activity Timeline</h2>
               {selectedCompetitorId && (
                   <span className="text-xs text-gray-500">
                       {events.length} events
                   </span>
               )}
            </div>
            <div className="flex-1 overflow-y-auto p-6">
                {!selectedCompetitorId ? (
                    <div className="h-full flex items-center justify-center text-gray-400">
                        Select a competitor to view their timeline
                    </div>
                ) : (
                    <EventTimeline events={events} loading={loadingEvents} />
                )}
            </div>
        </div>
      </div>
    </div>
  );
}