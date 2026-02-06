'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import api from '@/lib/api'; // Assuming api.ts exists and exports a default axios instance or similar
import { CompetitorRadarChart } from '@/components/CompetitorRadarChart';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'; // Assuming shadcn/ui Card components

interface RadarApiResponse {
  competitorName: string;
  data: Array<{
    attribute: string;
    score: number;
    fullMark: number; // Assuming fullMark comes from API or is set to 100
  }>;
}

interface RadarChartDataPoint {
  subject: string;
  A: number;
  fullMark: number;
}

export default function RadarPage() {
  const params = useParams();
  const competitorId = params.id as string;
  const [radarData, setRadarData] = useState<RadarChartDataPoint[]>([]);
  const [competitorName, setCompetitorName] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!competitorId) {
      setError('Competitor ID is missing.');
      setLoading(false);
      return;
    }

    const fetchRadarData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await api.get<RadarApiResponse>(`/api/v1/competitors/${competitorId}/radar`);
        setCompetitorName(response.data.competitorName || `Competitor ${competitorId}`);
        const formattedData: RadarChartDataPoint[] = response.data.data.map(item => ({
          subject: item.attribute,
          A: item.score,
          fullMark: item.fullMark || 100, // Default to 100 if not provided by API
        }));
        setRadarData(formattedData);
      } catch (err: any) {
        console.error('Error fetching radar data:', err);
        setError(err.response?.data?.detail || 'Failed to fetch radar data.');
      } finally {
        setLoading(false);
      }
    };

    fetchRadarData();
  }, [competitorId]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <p>Loading Radar Chart...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-screen text-red-500">
        <p>Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>Competitive Radar for {competitorName}</CardTitle>
        </CardHeader>
        <CardContent>
          <CompetitorRadarChart data={radarData} competitorName={competitorName} />
        </CardContent>
      </Card>
    </div>
  );
}
