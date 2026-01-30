'use client';

import React, { useEffect, useState } from 'react';
import { 
  Mail, 
  Slack, 
  MessageSquare, 
  Phone, 
  Save, 
  Loader2, 
  Bell, 
  Webhook, 
  Smartphone,
  AlertTriangle,
  Lock
} from 'lucide-react';
import api from '@/lib/api';
import { toast } from 'sonner';
import { useAuth } from '@/context/AuthContext';

// Notification channel types matching backend Enum
type NotificationChannel = 'email' | 'sms' | 'webhook' | 'in_app' | 'slack' | 'discord' | 'whatsapp';

interface NotificationSetting {
  id: string;
  user_id: string;
  channel: NotificationChannel;
  min_score: number;
  enabled: boolean;
  destination: string | null;
}

// Channel configuration for UI
const channelConfig: Record<NotificationChannel, {
  label: string;
  icon: any;
  description: string;
  destinationLabel?: string;
  destinationPlaceholder?: string;
  premium?: boolean;
  color: string;
  bgColor: string;
}> = {
  in_app: {
    label: 'In-App',
    icon: Bell,
    description: 'Show alerts within the dashboard notification center',
    color: 'text-orange-600',
    bgColor: 'bg-orange-100 dark:bg-orange-900/30',
  },
  email: {
    label: 'Email',
    icon: Mail,
    description: 'Receive email notifications for high-threat events',
    destinationLabel: 'Email Address',
    destinationPlaceholder: 'user@example.com',
    color: 'text-blue-600',
    bgColor: 'bg-blue-100 dark:bg-blue-900/30',
  },
  slack: {
    label: 'Slack',
    icon: Slack,
    description: 'Post notifications to your Slack workspace',
    destinationLabel: 'Webhook URL',
    destinationPlaceholder: 'https://hooks.slack.com/services/...',
    color: 'text-purple-600',
    bgColor: 'bg-purple-100 dark:bg-purple-900/30',
  },
  discord: {
    label: 'Discord',
    icon: MessageSquare,
    description: 'Send notifications to your Discord server',
    destinationLabel: 'Webhook URL',
    destinationPlaceholder: 'https://discord.com/api/webhooks/...',
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-100 dark:bg-indigo-900/30',
  },
  webhook: {
    label: 'Custom Webhook',
    icon: Webhook,
    description: 'Send raw JSON payloads to any HTTP endpoint',
    destinationLabel: 'Endpoint URL',
    destinationPlaceholder: 'https://api.yourdomain.com/webhooks/alerts',
    color: 'text-gray-600',
    bgColor: 'bg-gray-100 dark:bg-gray-800',
  },
  sms: {
    label: 'SMS Alerts',
    icon: Smartphone,
    description: 'Get text message alerts (Ultimate Plan only)',
    destinationLabel: 'Phone Number',
    destinationPlaceholder: '+1234567890',
    premium: true,
    color: 'text-rose-600',
    bgColor: 'bg-rose-100 dark:bg-rose-900/30',
  },
  whatsapp: {
    label: 'WhatsApp',
    icon: Phone,
    description: 'Urgent WhatsApp alerts (Ultimate Plan only)',
    destinationLabel: 'Phone Number',
    destinationPlaceholder: '+1234567890',
    premium: true,
    color: 'text-green-600',
    bgColor: 'bg-green-100 dark:bg-green-900/30',
  },
};

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
      focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600 focus-visible:ring-offset-2
      disabled:cursor-not-allowed disabled:opacity-50
      ${checked ? 'bg-indigo-600' : 'bg-gray-300 dark:bg-gray-600'}
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

export default function SettingsPage() {
  const { user } = useAuth();
  const [settings, setSettings] = useState<NotificationSetting[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState<Record<string, boolean>>({});

  const isUltimate = user?.plan_type === 'ultimate';

  useEffect(() => {
    const loadSettings = async () => {
      try {
        setLoading(true);
        const response = await api.get<NotificationSetting[]>('/api/v1/notifications/users/me/notifications');
        
        // If user has no settings yet, they might need initialization
        if (response.data.length === 0) {
            const resetResponse = await api.post<NotificationSetting[]>('/api/v1/notifications/users/me/notifications/reset');
            setSettings(resetResponse.data);
        } else {
            setSettings(response.data);
        }
      } catch (error) {
        console.error('Error loading notification settings:', error);
        toast.error('Failed to load notification settings');
      } finally {
        setLoading(false);
      }
    };

    loadSettings();
  }, []);

  const updateSetting = (channel: NotificationChannel, updates: Partial<NotificationSetting>) => {
    setSettings((prev) => 
      prev.map((s) => s.channel === channel ? { ...s, ...updates } : s)
    );
    setHasChanges((prev) => ({ ...prev, [channel]: true }));
  };

  const saveChannel = async (channel: NotificationChannel) => {
    const setting = settings.find(s => s.channel === channel);
    if (!setting) return;

    try {
      setSaving(true);
      await api.patch(`/api/v1/notifications/users/me/notifications/${channel}`, {
        min_score: setting.min_score,
        enabled: setting.enabled,
        destination: setting.destination
      });
      setHasChanges((prev) => ({ ...prev, [channel]: false }));
      toast.success(`${channelConfig[channel].label} settings saved`);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || `Failed to save ${channel} settings`);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Notification Settings
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Configure how you want to be alerted when competitor movements are detected.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {settings.map((setting) => {
          const config = channelConfig[setting.channel];
          if (!config) return null;

          const isRestricted = config.premium && !isUltimate;
          const Icon = config.icon;
          const changed = hasChanges[setting.channel];

          return (
            <div 
              key={setting.channel}
              className={`
                bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm
                overflow-hidden transition-all
                ${isRestricted ? 'opacity-75 grayscale-[0.5]' : ''}
              `}
            >
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex gap-4">
                    <div className={`p-3 rounded-xl ${config.bgColor}`}>
                      <Icon className={`h-6 w-6 ${config.color}`} />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                          {config.label}
                        </h3>
                        {config.premium && (
                          <span className={`
                            flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full
                            ${isUltimate ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}
                          `}>
                            {isUltimate ? 'Unlocked' : 'Ultimate'}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {config.description}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex flex-col items-end gap-2">
                    <ToggleSwitch
                      checked={setting.enabled}
                      onChange={(enabled) => updateSetting(setting.channel, { enabled })}
                      disabled={isRestricted || saving}
                    />
                    {changed && (
                      <button
                        onClick={() => saveChannel(setting.channel)}
                        disabled={saving}
                        className="text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
                      >
                        <Save className="h-3 w-3" />
                        Save
                      </button>
                    )}
                  </div>
                </div>

                {isRestricted ? (
                  <div className="mt-6 p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg flex gap-3">
                    <Lock className="h-5 w-5 text-amber-600 shrink-0" />
                    <div>
                      <p className="text-sm font-semibold text-amber-800 dark:text-amber-200">
                        Channel Locked
                      </p>
                      <p className="text-xs text-amber-700 dark:text-amber-300">
                        SMS and WhatsApp notifications are only available on the Ultimate plan. 
                        Upgrade your account to unlock these channels.
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className={`mt-8 space-y-6 ${!setting.enabled ? 'pointer-events-none opacity-50' : ''}`}>
                    {/* Destination Input */}
                    {config.destinationLabel && (
                      <div className="space-y-2">
                        <label className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                          {config.destinationLabel}
                        </label>
                        <input
                          type="text"
                          value={setting.destination || ''}
                          onChange={(e) => updateSetting(setting.channel, { destination: e.target.value })}
                          placeholder={config.destinationPlaceholder}
                          className="
                            w-full px-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg
                            text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-indigo-600 outline-none
                          "
                        />
                      </div>
                    )}

                    {/* Min Score Selector */}
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <label className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                          Minimum Threat Score Threshold
                        </label>
                        <span className="px-2 py-1 bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 text-xs font-bold rounded">
                          {setting.min_score}+
                        </span>
                      </div>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        step="5"
                        value={setting.min_score}
                        onChange={(e) => updateSetting(setting.channel, { min_score: parseInt(e.target.value) })}
                        className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                      />
                      <div className="flex justify-between text-[10px] text-gray-400 font-medium">
                        <span>Low Noise (0)</span>
                        <span>Critical Only (100)</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 p-6 rounded-xl flex gap-4">
        <AlertTriangle className="h-6 w-6 text-blue-600 shrink-0" />
        <div>
          <h4 className="font-bold text-blue-900 dark:text-blue-100">
            About Notification Scores
          </h4>
          <p className="text-sm text-blue-800 dark:text-blue-200 mt-1">
            Vigilux assigns a score (0-100) to every competitor event. 
            Setting a higher threshold ensures you only get notified about major breakthroughs, while a lower threshold keeps you informed of every minor change.
          </p>
        </div>
      </div>
    </div>
  );
}