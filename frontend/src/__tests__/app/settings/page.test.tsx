import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '../../utils/test-utils'
import SettingsPage from '@/app/dashboard/settings/page'
import { server } from '../../mocks/server'
import { HttpResponse } from 'msw'
import { toast } from 'sonner'

vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

describe('SettingsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    server.listen()
  })

  describe('loading state', () => {
    it('should show loading spinner on initial load', () => {
      render(<SettingsPage />)

      const spinner = document.querySelector('.animate-spin')
      expect(spinner).toBeInTheDocument()
    })

    it('should not render content while loading', () => {
      render(<SettingsPage />)

      expect(screen.queryByText('Notification Settings')).not.toBeInTheDocument()
    })
  })

  describe('initial render', () => {
    it('should render page title and description', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText('Notification Settings')).toBeInTheDocument()
        expect(screen.getByText('Configure how and when you receive threat notifications')).toBeInTheDocument()
      })
    })

    it('should render all channel cards', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText('Email')).toBeInTheDocument()
        expect(screen.getByText('Slack')).toBeInTheDocument()
        expect(screen.getByText('Discord')).toBeInTheDocument()
        expect(screen.getByText('WhatsApp')).toBeInTheDocument()
      })
    })

    it('should render toggle switches for each channel', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        const toggles = document.querySelectorAll('[class*="translate-x-"]')
        expect(toggles.length).toBe(4)
      })
    })

    it('should render min score sliders', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getAllByText('Minimum Threat Score').length).toBe(4)
      })
    })
  })

  describe('channel interactions', () => {
    it('should toggle channel enabled state', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText('Notification Settings')).toBeInTheDocument()
      })

      const slackToggle = document.querySelectorAll('button[class*="inline-flex"]')[1]
      fireEvent.click(slackToggle)

      await waitFor(() => {
        expect(screen.getByText('Save Changes')).toBeInTheDocument()
      })
    })

    it('should update min score when slider changes', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText('Notification Settings')).toBeInTheDocument()
      })

      const sliders = document.querySelectorAll('input[type="range"]')
      const emailSlider = sliders[0]

      fireEvent.change(emailSlider, { target: { value: '85' } })

      await waitFor(() => {
        expect(screen.getByText('Save Changes')).toBeInTheDocument()
        expect(screen.getByText('85')).toBeInTheDocument()
      })
    })

    it('should disable slider when channel is disabled', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText('Notification Settings')).toBeInTheDocument()
      })

      const sliders = document.querySelectorAll('input[type="range"]')
      const slackSlider = sliders[1] // Slack is disabled by default

      expect(slackSlider).toBeDisabled()
    })
  })

  describe('webhook inputs', () => {
    it('should render webhook URL input for Slack', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText('Notification Settings')).toBeInTheDocument()
      })

      expect(screen.getByLabelText(/Webhook URL/)).toBeInTheDocument()
    })

    it('should render webhook URL input for Discord', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText('Notification Settings')).toBeInTheDocument()
      })

      const webhookInputs = screen.getAllByLabelText(/Webhook URL/)
      expect(webhookInputs.length).toBe(2)
    })

    it('should update webhook URL value', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText('Notification Settings')).toBeInTheDocument()
      })

      // First enable Slack
      const slackToggle = document.querySelectorAll('button[class*="inline-flex"]')[1]
      fireEvent.click(slackToggle)

      await waitFor(() => {
        const webhookInput = screen.getAllByLabelText(/Webhook URL/)[0]
        fireEvent.change(webhookInput, { target: { value: 'https://hooks.slack.com/test' } })
      })

      await waitFor(() => {
        expect(screen.getByText('Save Changes')).toBeInTheDocument()
      })
    })

    it('should disable webhook input when channel is disabled', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText('Notification Settings')).toBeInTheDocument()
      })

      const webhookInputs = screen.getAllByLabelText(/Webhook URL/)
      expect(webhookInputs[0]).toBeDisabled()
    })
  })

  describe('phone input', () => {
    it('should render phone number input for WhatsApp', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText('Notification Settings')).toBeInTheDocument()
      })

      expect(screen.getByLabelText(/Phone Number/)).toBeInTheDocument()
    })

    it('should update phone number value', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText('Notification Settings')).toBeInTheDocument()
      })

      // First enable WhatsApp
      const whatsappToggle = document.querySelectorAll('button[class*="inline-flex"]')[3]
      fireEvent.click(whatsappToggle)

      await waitFor(() => {
        const phoneInput = screen.getByLabelText(/Phone Number/)
        fireEvent.change(phoneInput, { target: { value: '+1234567890' } })
      })

      await waitFor(() => {
        expect(screen.getByText('Save Changes')).toBeInTheDocument()
      })
    })

    it('should disable phone input when WhatsApp is disabled', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText('Notification Settings')).toBeInTheDocument()
      })

      const phoneInput = screen.getByLabelText(/Phone Number/)
      expect(phoneInput).toBeDisabled()
    })
  })

  describe('save functionality', () => {
    it('should show save button when changes are made', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText('Notification Settings')).toBeInTheDocument()
      })

      const slackToggle = document.querySelectorAll('button[class*="inline-flex"]')[1]
      fireEvent.click(slackToggle)

      await waitFor(() => {
        expect(screen.getByText('Save Changes')).toBeInTheDocument()
      })
    })

    it('should show loading state while saving', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText('Notification Settings')).toBeInTheDocument()
      })

      const slackToggle = document.querySelectorAll('button[class*="inline-flex"]')[1]
      fireEvent.click(slackToggle)

      await waitFor(() => {
        const saveButton = screen.getByText('Save Changes')
        fireEvent.click(saveButton)
      })

      await waitFor(() => {
        expect(screen.getByText('Saving...')).toBeInTheDocument()
      })
    })

    it('should show success toast on save', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText('Notification Settings')).toBeInTheDocument()
      })

      const slackToggle = document.querySelectorAll('button[class*="inline-flex"]')[1]
      fireEvent.click(slackToggle)

      await waitFor(() => {
        const saveButton = screen.getByText('Save Changes')
        fireEvent.click(saveButton)
      })

      await waitFor(() => {
        expect(toast.success).toHaveBeenCalledWith('Notification settings saved successfully')
      })
    })

    it('should hide save button after successful save', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText('Notification Settings')).toBeInTheDocument()
      })

      const slackToggle = document.querySelectorAll('button[class*="inline-flex"]')[1]
      fireEvent.click(slackToggle)

      await waitFor(() => {
        const saveButton = screen.getByText('Save Changes')
        fireEvent.click(saveButton)
      })

      await waitFor(() => {
        expect(screen.queryByText('Save Changes')).not.toBeInTheDocument()
      })
    })
  })

  describe('unsaved changes warning', () => {
    it('should show unsaved changes warning', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText('Notification Settings')).toBeInTheDocument()
      })

      const slackToggle = document.querySelectorAll('button[class*="inline-flex"]')[1]
      fireEvent.click(slackToggle)

      await waitFor(() => {
        expect(screen.getByText('You have unsaved changes')).toBeInTheDocument()
      })
    })

    it('should hide warning after save', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText('Notification Settings')).toBeInTheDocument()
      })

      const slackToggle = document.querySelectorAll('button[class*="inline-flex"]')[1]
      fireEvent.click(slackToggle)

      await waitFor(() => {
        const saveButton = screen.getByText('Save Changes')
        fireEvent.click(saveButton)
      })

      await waitFor(() => {
        expect(screen.queryByText('You have unsaved changes')).not.toBeInTheDocument()
      })
    })
  })

  describe('error handling', () => {
    it('should show error toast on save failure', async () => {
      server.use(
        HttpResponse.json(
          { detail: 'Failed to save settings' },
          { status: 500 }
        )
      )

      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText('Notification Settings')).toBeInTheDocument()
      })

      const slackToggle = document.querySelectorAll('button[class*="inline-flex"]')[1]
      fireEvent.click(slackToggle)

      await waitFor(() => {
        const saveButton = screen.getByText('Save Changes')
        fireEvent.click(saveButton)
      })

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalled()
      })
    })
  })

  describe('channel descriptions', () => {
    it('should display email channel description', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText('Receive email notifications for high-threat events')).toBeInTheDocument()
      })
    })

    it('should display Slack channel description', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText('Post notifications to your Slack workspace')).toBeInTheDocument()
      })
    })

    it('should display Discord channel description', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText('Send notifications to your Discord server')).toBeInTheDocument()
      })
    })

    it('should display WhatsApp channel description', async () => {
      render(<SettingsPage />)

      await waitFor(() => {
        expect(screen.getByText('Get WhatsApp messages for urgent alerts')).toBeInTheDocument()
      })
    })
  })
})
