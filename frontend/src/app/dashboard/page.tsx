'use client';

import React, { useEffect, useState } from 'react';
import { Users, Zap, Activity, Loader2 } from 'lucide-react';
import api from '@/lib/api';
import { StatCard } from '@/components/dashboard/StatCard';
import { ThreatTimeline } from '@/components/dashboard/ThreatTimeline';
import { toast } from 'sonner';
import { useWebSocket } from '@/hooks/use-socket';

interface DashboardStats {
  total_competitors: number;
  breakthroughs_today: number;
  avg_threat_score: number;
  chart_data: Array<{ date: string; count: number }>;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  
  const [scanningCompetitor, setScanningCompetitor] = useState<string | null>(null);
  const { lastMessage } = useWebSocket();

  useEffect(() => {
    if (lastMessage?.type === 'TASK_UPDATE' && lastMessage.data) {
        const { status, competitor_name } = lastMessage.data;
        // Check for start statuses
        if (status === 'scraping_started' || status === 'analysis_started' || status === 'requested') {
            setScanningCompetitor(competitor_name || 'Competitor');
        } else if (status === 'analysis_complete' || String(status).includes('failed')) {
            // Add a small delay before hiding to ensure user sees completion if they are staring at it, 
            // but for a banner usually immediate removal or switching to "Done" is better. 
            // We'll remove it.
            setScanningCompetitor(null);
        }
    }
  }, [lastMessage]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/api/v1/dashboard/stats');
        setStats(response.data);
      } catch (error) {
        console.error('Failed to fetch dashboard stats:', error);
        toast.error('Failed to load dashboard statistics');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="p-8 space-y-8 animate-pulse">
         <div className="h-8 w-48 bg-gray-200 dark:bg-gray-800 rounded"></div>
         <div className="grid gap-6 md:grid-cols-3">
            {[1, 2, 3].map(i => <div key={i} className="h-32 bg-gray-200 dark:bg-gray-800 rounded"></div>)}
         </div>
         <div className="h-64 bg-gray-200 dark:bg-gray-800 rounded"></div>
      </div>
    );
  }

  if (!stats) {
    return <div className="p-8">Failed to load data.</div>;
  }

  return (
    <div className="space-y-8">
      {scanningCompetitor && (
        <div className="bg-blue-600 text-white px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 animate-in slide-in-from-top-2 duration-300">
            <Loader2 className="w-5 h-5 animate-spin" />
            <p className="font-medium">
                AI Engines are currently scanning <span className="font-bold">{scanningCompetitor}</span> for breakthroughs...
            </p>
        </div>
      )}

      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-2">
          Overview of your competitor landscape and threat activities.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <StatCard
          title="Total Competitors"
          value={stats.total_competitors}
          icon={Users}
          description="Active competitors tracked"
        />
        <StatCard
          title="Breakthroughs Today"
          value={stats.breakthroughs_today}
          icon={Zap}
          description="High impact events detected"
          className="dark:border-yellow-900/50"
        />
        <StatCard
          title="Avg Threat Score"
          value={stats.avg_threat_score.toFixed(1)}
          icon={Activity}
          description="Overall market threat level"
        />
      </div>

      <ThreatTimeline data={stats.chart_data} />
    </div>
  );
}