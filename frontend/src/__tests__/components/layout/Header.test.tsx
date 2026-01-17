import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@/__tests__/utils/test-utils'
import { Header } from '@/components/layout/Header'
import { useAuth } from '@/context/AuthContext'

vi.mock('@/context/AuthContext', () => ({
  useAuth: vi.fn(),
}))

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}))

describe('Header', () => {
  const mockLogout = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    mockLogout.mockClear()

    vi.mocked(useAuth).mockReturnValue({
      isAuthenticated: true,
      user: { id: '1', email: 'test@example.com', plan_type: 'growth', is_verified: true },
      login: vi.fn(),
      logout: mockLogout,
      loading: false,
      refreshUser: vi.fn(),
    })
  })

  describe('rendering', () => {
    it('should render the header with workspace name', () => {
      render(<Header />)

      expect(screen.getByText('My Workspace')).toBeInTheDocument()
    })

    it('should render the theme toggle', () => {
      render(<Header />)

      // The mode-toggle should be present (button with sun/moon icon)
      const themeToggle = document.querySelector('button[class*="rounded-md"]')
      expect(themeToggle).toBeInTheDocument()
    })

    it('should render the account dropdown button', () => {
      render(<Header />)

      const accountButton = screen.getByText('Account')
      expect(accountButton).toBeInTheDocument()
    })

    it('should render user icon in dropdown button', () => {
      render(<Header />)

      const userIcon = document.querySelector('.lucide-user')
      expect(userIcon).toBeInTheDocument()
    })
  })

  describe('dropdown behavior', () => {
    it('should not show dropdown content initially', () => {
      render(<Header />)

      expect(screen.queryByText('Sign out')).not.toBeInTheDocument()
      expect(screen.queryByText('Settings')).not.toBeInTheDocument()
    })

    it('should open dropdown when account button is clicked', async () => {
      render(<Header />)

      const accountButton = screen.getByText('Account')
      fireEvent.click(accountButton)

      await waitFor(() => {
        expect(screen.getByText('Sign out')).toBeInTheDocument()
        expect(screen.getByText('Settings')).toBeInTheDocument()
      })
    })

    it('should close dropdown when clicking outside', async () => {
      render(<Header />)

      // Open dropdown
      const accountButton = screen.getByText('Account')
      fireEvent.click(accountButton)

      await waitFor(() => {
        expect(screen.getByText('Sign out')).toBeInTheDocument()
      })

      // Click outside
      fireEvent.mouseDown(document.body)

      await waitFor(() => {
        expect(screen.queryByText('Sign out')).not.toBeInTheDocument()
      })
    })

    it('should toggle dropdown when account button is clicked multiple times', async () => {
      render(<Header />)

      const accountButton = screen.getByText('Account')

      // Open dropdown
      fireEvent.click(accountButton)
      await waitFor(() => {
        expect(screen.getByText('Sign out')).toBeInTheDocument()
      })

      // Close dropdown
      fireEvent.click(accountButton)
      await waitFor(() => {
        expect(screen.queryByText('Sign out')).not.toBeInTheDocument()
      })
    })
  })

  describe('dropdown actions', () => {
    it('should call logout when sign out button is clicked', async () => {
      render(<Header />)

      // Open dropdown
      const accountButton = screen.getByText('Account')
      fireEvent.click(accountButton)

      await waitFor(() => {
        expect(screen.getByText('Sign out')).toBeInTheDocument()
      })

      // Click sign out
      const signOutButton = screen.getByText('Sign out')
      fireEvent.click(signOutButton)

      expect(mockLogout).toHaveBeenCalledOnce()

      await waitFor(() => {
        expect(screen.queryByText('Sign out')).not.toBeInTheDocument()
      })
    })

    it('should close dropdown after logout', async () => {
      render(<Header />)

      // Open dropdown
      const accountButton = screen.getByText('Account')
      fireEvent.click(accountButton)

      await waitFor(() => {
        expect(screen.getByText('Sign out')).toBeInTheDocument()
      })

      // Click sign out
      const signOutButton = screen.getByText('Sign out')
      fireEvent.click(signOutButton)

      await waitFor(() => {
        expect(screen.queryByText('Sign out')).not.toBeInTheDocument()
      })
    })

    it('should render settings link', async () => {
      render(<Header />)

      // Open dropdown
      const accountButton = screen.getByText('Account')
      fireEvent.click(accountButton)

      await waitFor(() => {
        const settingsLink = screen.getByText('Settings').closest('a')
        expect(settingsLink).toHaveAttribute('href', '/settings')
      })
    })

    it('should close dropdown when settings link is clicked', async () => {
      render(<Header />)

      // Open dropdown
      const accountButton = screen.getByText('Account')
      fireEvent.click(accountButton)

      await waitFor(() => {
        expect(screen.getByText('Settings')).toBeInTheDocument()
      })

      // Click settings link
      const settingsLink = screen.getByText('Settings').closest('a')
      fireEvent.click(settingsLink!)

      await waitFor(() => {
        expect(screen.queryByText('Sign out')).not.toBeInTheDocument()
      })
    })
  })

  describe('dropdown content', () => {
    it('should display user information in dropdown', async () => {
      render(<Header />)

      const accountButton = screen.getByText('Account')
      fireEvent.click(accountButton)

      await waitFor(() => {
        expect(screen.getByText('User')).toBeInTheDocument()
        expect(screen.getByText('user@example.com')).toBeInTheDocument()
      })
    })

    it('should render logout icon in sign out button', async () => {
      render(<Header />)

      const accountButton = screen.getByText('Account')
      fireEvent.click(accountButton)

      await waitFor(() => {
        const logoutIcon = document.querySelector('.lucide-log-out')
        expect(logoutIcon).toBeInTheDocument()
      })
    })
  })

  describe('responsive design', () => {
    it('should hide workspace name on small screens', () => {
      render(<Header />)

      const workspaceText = screen.getByText('My Workspace')
      expect(workspaceText).toHaveClass('hidden', 'lg:block')
    })

    it('should hide account text on small screens', () => {
      render(<Header />)

      const accountText = screen.getByText('Account')
      expect(accountText).toHaveClass('hidden', 'sm:block')
    })
  })
})
