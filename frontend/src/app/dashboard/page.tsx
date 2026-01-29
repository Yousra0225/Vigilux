'use client';

import React, { useEffect, useState } from 'react';
import { Users, Zap, Activity } from 'lucide-react';
import api from '@/lib/api';
import { StatCard } from '@/components/dashboard/StatCard';
import { ThreatTimeline } from '@/components/dashboard/ThreatTimeline';
import { toast } from 'sonner';

interface DashboardStats {
  total_competitors: number;
  breakthroughs_today: number;
  avg_threat_score: number;
  chart_data: Array<{ date: string; count: number }>;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

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