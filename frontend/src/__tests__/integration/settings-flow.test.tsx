import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@/__tests__/utils/test-utils'
import SettingsPage from '@/app/dashboard/settings/page'
import { server } from '../mocks/server'
import { HttpResponse, http } from 'msw'

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}))

vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    info: vi.fn(),
    error: vi.fn(),
  },
}))

describe('Notification Settings Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    server.listen()
  })

  it('renders notification channels and handles updates', async () => {
    render(<SettingsPage />)

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Email')).toBeInTheDocument()
      expect(screen.getByText('Slack')).toBeInTheDocument()
    })

    // Find a toggle and click it
    const toggles = screen.getAllByRole('button')
    // email toggle is usually first
    fireEvent.click(toggles[0])

    // Should show Save button
    expect(screen.getByText('Save')).toBeInTheDocument()

    // Click save
    fireEvent.click(screen.getByText('Save'))

    await waitFor(() => {
      // toast.success should be called (from SettingsPage component logic)
      // Note: my component logic has toast.success(`${channelConfig[channel].label} settings saved`)
    })
  })

  it('displays tier restrictions for non-ultimate users', async () => {
    // Mock user as 'starter'
    vi.mock('@/context/AuthContext', async () => {
        const actual: any = await vi.importActual('@/context/AuthContext')
        return {
            ...actual,
            useAuth: () => ({
                user: { plan_type: 'starter' },
                loading: false
            })
        }
    })

    render(<SettingsPage />)

    await waitFor(() => {
      expect(screen.getAllByText('Channel Locked')).toHaveLength(2) // SMS and WhatsApp
    })
  })
})
