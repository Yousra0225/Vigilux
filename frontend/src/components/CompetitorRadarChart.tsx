'use client';

import React from 'react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';

interface RadarData {
  subject: string;
  A: number; // Score for the current competitor
  fullMark: number; // Max possible score, typically 100
}

interface CompetitorRadarChartProps {
  data: RadarData[];
  competitorName?: string;
}

export function CompetitorRadarChart({ data, competitorName = 'Competitor' }: CompetitorRadarChartProps) {
  if (!data || data.length === 0) {
    return <div className="flex items-center justify-center h-full text-gray-500">No radar data available.</div>;
  }

  // Determine the max value for PolarRadiusAxis dynamically or set a fixed one
  const maxScore = data.reduce((max, item) => Math.max(max, item.A), 0);
  const chartDomain = [0, maxScore > 0 ? Math.ceil(maxScore / 10) * 10 : 100]; // Ensure fullMark is covered, round up to nearest 10

  return (
    <ResponsiveContainer width="100%" height={400}>
      <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
        <PolarGrid />
        <PolarAngleAxis dataKey="subject" />
        {/* PolarRadiusAxis can be dynamic based on data, or fixed. Using fixed for simplicity unless specified. */}
        <PolarRadiusAxis domain={chartDomain} />
        <Radar
          name={competitorName}
          dataKey="A"
          stroke="#8884d8"
          fill="#8884d8"
          fillOpacity={0.6}
        />
        <Tooltip />
        <Legend />
      </RadarChart>
    </ResponsiveContainer>
  );
}
