'use client';

import React from 'react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip
} from 'recharts';

interface RadarDataPoint {
  subject: string;
  A: number; // Score for the competitor
  fullMark: number;
}

interface CompetitorRadarChartProps {
  data: RadarDataPoint[];
  color?: string;
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white dark:bg-gray-800 p-3 border border-gray-200 dark:border-gray-700 shadow-lg rounded-lg">
        <p className="font-bold text-gray-900 dark:text-white mb-1">{label}</p>
        <p className="text-sm text-blue-600 dark:text-blue-400">
          Score: <span className="font-mono font-bold">{payload[0].value}</span> / 100
        </p>
      </div>
    );
  }
  return null;
};

export function CompetitorRadarChart({ data, color = '#2563eb' }: CompetitorRadarChartProps) {
  return (
    <div className="w-full h-[300px] sm:h-[400px] bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm p-4">
      <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 text-center">
        Threat Analysis Visualization
      </h3>
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
          <PolarGrid stroke="#e5e7eb" strokeDasharray="3 3" />
          <PolarAngleAxis 
            dataKey="subject" 
            tick={{ fill: '#6b7280', fontSize: 12 }} 
          />
          <PolarRadiusAxis 
            angle={30} 
            domain={[0, 100]} 
            tick={{ fill: '#9ca3af', fontSize: 10 }}
            tickCount={6}
          />
          <Radar
            name="Competitor"
            dataKey="A"
            stroke={color}
            strokeWidth={3}
            fill={color}
            fillOpacity={0.4}
            dot={{ r: 4, fill: color, strokeWidth: 0 }}
            activeDot={{ r: 6, strokeWidth: 0 }}
          />
          <Tooltip content={<CustomTooltip />} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
