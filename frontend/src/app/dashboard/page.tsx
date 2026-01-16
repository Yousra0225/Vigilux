'use client';

import React, { useEffect, useState } from 'react';
import { Users, AlertTriangle, Activity } from 'lucide-react';
import api from '@/lib/api';
import { StatCard } from '@/components/dashboard/StatCard';
import { ThreatTimeline } from '@/components/dashboard/ThreatTimeline';
import { toast } from 'sonner';

interface TimelinePoint {
  date: string;
  count: number;
}

interface DashboardStats {
  total_competitors: number;
  breakthrough_signals_count: number;
  average_threat_score: number;
  timeline_data: TimelinePoint[];
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
        console.error('Error fetching dashboard stats:', error);
        toast.error('Failed to load dashboard statistics');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
      </div>
    );
  }

  if (!stats) {
     return (
        <div className="p-6">
           <p className="text-center text-gray-500">No data available.</p>
        </div>
     );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          title="Total Competitors"
          value={stats.total_competitors}
          icon={Users}
          description="Active competitors being tracked"
        />
        <StatCard
          title="Breakthrough Signals"
          value={stats.breakthrough_signals_count}
          icon={Activity}
          description="High impact events detected"
        />
        <StatCard
          title="Avg Threat Score"
          value={stats.average_threat_score}
          icon={AlertTriangle}
          description="Overall threat level"
        />
      </div>

      <div className="mt-6">
        <ThreatTimeline data={stats.timeline_data} />
      </div>
    </div>
  );
}
