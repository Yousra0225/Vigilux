'use client';

import React, { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import api from '@/lib/api';
import { toast } from 'sonner';
import { Check } from 'lucide-react';


const NICHES = [
  'E-commerce',
  'SaaS',
  'Digital Agency',
  'Real Estate',
  'Healthcare',
  'Finance',
  'Education',
  'Content Creation',
  'Other'
];

export function NicheSelectionModal() {
  const { user, refreshUser } = useAuth();
  const [selectedNiche, setSelectedNiche] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // If user already has a niche or user is not loaded, don't show
  if (!user || user.niche) {
    return null;
  }

  const handleSave = async () => {
    if (!selectedNiche) return;

    setIsSubmitting(true);
    try {
      await api.patch('/api/v1/auth/me', { niche: selectedNiche });
      await refreshUser();
      toast.success('Niche saved successfully');
    } catch (error) {
      console.error('Failed to save niche:', error);
      toast.error('Failed to save niche. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-md bg-white dark:bg-gray-800 rounded-xl shadow-2xl overflow-hidden border border-gray-200 dark:border-gray-700">
        <div className="p-6 text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Select Your Industry
          </h2>
          <p className="text-gray-500 dark:text-gray-400 mb-6">
            Help us tailor your experience by selecting your business domain.
          </p>

          <div className="grid grid-cols-2 gap-3 mb-8">
            {NICHES.map((niche) => (
              <button
                key={niche}
                onClick={() => setSelectedNiche(niche)}
                className={`
                  relative flex items-center justify-center p-3 rounded-lg border text-sm font-medium transition-all
                  ${selectedNiche === niche
                    ? 'border-blue-600 bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:border-blue-500 dark:text-blue-300'
                    : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-700/50 dark:text-gray-300'}
                `}
              >
                {niche}
                {selectedNiche === niche && (
                  <div className="absolute top-1 right-1 text-blue-600 dark:text-blue-400">
                    <Check className="w-3 h-3" />
                  </div>
                )}
              </button>
            ))}
          </div>

          <button
            onClick={handleSave}
            disabled={!selectedNiche || isSubmitting}
            className={`
              w-full py-2.5 px-4 rounded-lg text-white font-medium transition-colors
              ${!selectedNiche || isSubmitting
                ? 'bg-gray-300 dark:bg-gray-700 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 shadow-sm'}
            `}
          >
            {isSubmitting ? 'Saving...' : 'Continue to Dashboard'}
          </button>
        </div>
      </div>
    </div>
  );
}
