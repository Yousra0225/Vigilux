'use client';

import React, { useEffect, useState } from 'react';
import { Mail, Slack, MessageSquare, Phone, Save, Loader2 } from 'lucide-react';
import api from '@/lib/api';
import { toast } from 'sonner';

// Notification channel configuration types
interface NotificationChannel {
  enabled: boolean;
  min_score: number;
  webhook_url?: string;
  phone_number?: string;
}

interface NotificationSettings {
  email: NotificationChannel;
  slack: NotificationChannel;
  discord: NotificationChannel;
  whatsapp: NotificationChannel;
}

// Default settings structure
const defaultSettings: NotificationSettings = {
  email: { enabled: false, min_score: 70 },
  slack: { enabled: false, min_score: 70, webhook_url: '' },
  discord: { enabled: false, min_score: 70, webhook_url: '' },
  whatsapp: { enabled: false, min_score: 70, phone_number: '' },
};

// Channel configuration for UI
const channelConfig = [
  {
    key: 'email' as const,
    label: 'Email',
    icon: Mail,
    description: 'Receive email notifications for high-threat events',
    hasWebhook: false,
    hasPhone: false,
    color: 'text-blue-600',
    bgColor: 'bg-blue-100 dark:bg-blue-900/30',
  },
  {
    key: 'slack' as const,
    label: 'Slack',
    icon: Slack,
    description: 'Post notifications to your Slack workspace',
    hasWebhook: true,
    hasPhone: false,
    color: 'text-purple-600',
    bgColor: 'bg-purple-100 dark:bg-purple-900/30',
  },
  {
    key: 'discord' as const,
    label: 'Discord',
    icon: MessageSquare,
    description: 'Send notifications to your Discord server',
    hasWebhook: true,
    hasPhone: false,
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-100 dark:bg-indigo-900/30',
  },
  {
    key: 'whatsapp' as const,
    label: 'WhatsApp',
    icon: Phone,
    description: 'Get WhatsApp messages for urgent alerts',
    hasWebhook: false,
    hasPhone: true,
    color: 'text-green-600',
    bgColor: 'bg-green-100 dark:bg-green-900/30',
  },
];

// Toggle switch component
const ToggleSwitch: React.FC<{
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
}> = ({ checked, onChange, disabled }) => (
  <button
    type="button"
    onClick={() => onChange(!checked)}
    disabled={disabled}
    className={`
      relative inline-flex h-6 w-11 items-center rounded-full transition-colors
      focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2
      disabled:cursor-not-allowed disabled:opacity-50
      ${checked ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'}
    `}
  >
    <span
      className={`
        inline-block h-4 w-4 transform rounded-full bg-white transition-transform
        ${checked ? 'translate-x-6' : 'translate-x-1'}
      `}
    />
  </button>
);

// Slider component
const ScoreSlider: React.FC<{
  value: number;
  onChange: (value: number) => void;
  disabled?: boolean;
}> = ({ value, onChange, disabled }) => (
  <div className="flex items-center gap-4 flex-1">
    <input
      type="range"
      min="0"
      max="100"
      value={value}
      onChange={(e) => onChange(parseInt(e.target.value))}
      disabled={disabled}
      className="
        flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer
        accent-blue-600 disabled:cursor-not-allowed disabled:opacity-50
        [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4
        [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-blue-600
        [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:disabled:opacity-50
      "
    />
    <span className="text-sm font-semibold text-gray-900 dark:text-white w-12 text-center">
      {value}
    </span>
  </div>
);

// Channel card component
const ChannelCard: React.FC<{
  config: typeof channelConfig[0];
  channel: NotificationChannel;
  onChange: (updates: Partial<NotificationChannel>) => void;
  disabled: boolean;
}> = ({ config, channel, onChange, disabled }) => {
  const Icon = config.icon;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${config.bgColor}`}>
            <Icon className={`h-5 w-5 ${config.color}`} />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {config.label}
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {config.description}
            </p>
          </div>
        </div>
        <ToggleSwitch
          checked={channel.enabled}
          onChange={(checked) => onChange({ enabled: checked })}
          disabled={disabled}
        />
      </div>

      {/* Min Score Slider */}
      <div className={`${!channel.enabled ? 'opacity-50' : ''} transition-opacity`}>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Minimum Threat Score
        </label>
        <ScoreSlider
          value={channel.min_score}
          onChange={(value) => onChange({ min_score: value })}
          disabled={disabled || !channel.enabled}
        />
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          Only send notifications when threat score is at or above this threshold
        </p>
      </div>

      {/* Webhook URL Input */}
      {config.hasWebhook && (
        <div className={`${!channel.enabled ? 'opacity-50' : ''} transition-opacity`}>
          <label htmlFor={`${config.key}-webhook`} className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Webhook URL <span className="text-gray-400">(optional)</span>
          </label>
          <input
            id={`${config.key}-webhook`}
            type="url"
            value={channel.webhook_url || ''}
            onChange={(e) => onChange({ webhook_url: e.target.value })}
            disabled={disabled || !channel.enabled}
            placeholder={`https://hooks.${config.key}.com/...`}
            className="
              w-full px-3 py-2 bg-gray-50 dark:bg-gray-700
              border border-gray-300 dark:border-gray-600 rounded-lg
              text-gray-900 dark:text-white placeholder-gray-400
              focus:ring-2 focus:ring-blue-600 focus:border-transparent
              disabled:cursor-not-allowed disabled:opacity-50
              transition-colors
            "
          />
        </div>
      )}

      {/* Phone Number Input */}
      {config.hasPhone && (
        <div className={`${!channel.enabled ? 'opacity-50' : ''} transition-opacity`}>
          <label htmlFor={`${config.key}-phone`} className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Phone Number <span className="text-gray-400">(optional)</span>
          </label>
          <input
            id={`${config.key}-phone`}
            type="tel"
            value={channel.phone_number || ''}
            onChange={(e) => onChange({ phone_number: e.target.value })}
            disabled={disabled || !channel.enabled}
            placeholder="+1234567890"
            className="
              w-full px-3 py-2 bg-gray-50 dark:bg-gray-700
              border border-gray-300 dark:border-gray-600 rounded-lg
              text-gray-900 dark:text-white placeholder-gray-400
              focus:ring-2 focus:ring-blue-600 focus:border-transparent
              disabled:cursor-not-allowed disabled:opacity-50
              transition-colors
            "
          />
        </div>
      )}
    </div>
  );
};

export default function SettingsPage() {
  const [settings, setSettings] = useState<NotificationSettings>(defaultSettings);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  // Load settings on mount
  useEffect(() => {
    const loadSettings = async () => {
      try {
        setLoading(true);
        const response = await api.get<NotificationSettings>('/api/v1/users/me/notifications');
        setSettings(response.data);
      } catch (error) {
        console.error('Error loading notification settings:', error);
        toast.error('Failed to load notification settings');
      } finally {
        setLoading(false);
      }
    };

    loadSettings();
  }, []);

  // Update a specific channel's settings
  const updateChannel = (key: keyof NotificationSettings, updates: Partial<NotificationChannel>) => {
    setSettings((prev) => ({
      ...prev,
      [key]: { ...prev[key], ...updates },
    }));
    setHasChanges(true);
  };

  // Save settings
  const saveSettings = async () => {
    try {
      setSaving(true);
      await api.patch('/api/v1/users/me/notifications', settings);
      setHasChanges(false);
      toast.success('Notification settings saved successfully');
    } catch (error: any) {
      console.error('Error saving notification settings:', error);
      const detail = error.response?.data?.detail || 'Failed to save notification settings';
      toast.error(detail);
    } finally {
      setSaving(false);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Notification Settings
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Configure how and when you receive threat notifications
          </p>
        </div>

        {/* Save Button */}
        {hasChanges && (
          <button
            onClick={saveSettings}
            disabled={saving}
            className="
              flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700
              text-white font-medium rounded-lg transition-colors
              disabled:cursor-not-allowed disabled:opacity-50
            "
          >
            {saving ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="h-4 w-4" />
                Save Changes
              </>
            )}
          </button>
        )}
      </div>

      {/* Channel Cards */}
      <div className="grid grid-cols-1 gap-6">
        {channelConfig.map((config) => (
          <ChannelCard
            key={config.key}
            config={config}
            channel={settings[config.key]}
            onChange={(updates) => updateChannel(config.key, updates)}
            disabled={saving}
          />
        ))}
      </div>

      {/* Unsaved Changes Warning */}
      {hasChanges && !saving && (
        <div className="fixed bottom-4 right-4 bg-yellow-100 dark:bg-yellow-900/30 border border-yellow-300 dark:border-yellow-700 text-yellow-800 dark:text-yellow-200 px-4 py-3 rounded-lg shadow-lg">
          <p className="text-sm font-medium">You have unsaved changes</p>
        </div>
      )}
    </div>
  );
}
