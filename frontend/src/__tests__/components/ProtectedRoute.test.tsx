import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@/__tests__/utils/test-utils'
import ProtectedRoute from '@/components/ProtectedRoute'
import { useAuth } from '@/context/AuthContext'

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}))

vi.mock('@/context/AuthContext', () => ({
  useAuth: vi.fn(),
}))

const mockUseAuth = vi.mocked(useAuth)

describe('ProtectedRoute', () => {
  const TestComponent = () => <div data-testid="protected-content">Protected Content</div>

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('loading state', () => {
    it('should show loading spinner while authenticating', () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: false,
        user: null,
        login: vi.fn(),
        logout: vi.fn(),
        loading: true,
        refreshUser: vi.fn(),
      })

      render(
        <ProtectedRoute>
          <TestComponent />
        </ProtectedRoute>
      )

      const spinner = screen.getByRole('status') || document.querySelector('.animate-spin')
      expect(spinner).toBeInTheDocument()
    })

    it('should not render children while loading', () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: false,
        user: null,
        login: vi.fn(),
        logout: vi.fn(),
        loading: true,
        refreshUser: vi.fn(),
      })

      render(
        <ProtectedRoute>
          <TestComponent />
        </ProtectedRoute>
      )

      expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument()
    })
  })

  describe('authenticated state', () => {
    it('should render children when authenticated', async () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        user: { id: '1', email: 'test@example.com', plan_type: 'growth', is_verified: true },
        login: vi.fn(),
        logout: vi.fn(),
        loading: false,
        refreshUser: vi.fn(),
      })

      render(
        <ProtectedRoute>
          <TestComponent />
        </ProtectedRoute>
      )

      await waitFor(() => {
        expect(screen.getByTestId('protected-content')).toBeInTheDocument()
      })
    })

    it('should not show loading spinner when authenticated', async () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        user: { id: '1', email: 'test@example.com', plan_type: 'growth', is_verified: true },
        login: vi.fn(),
        logout: vi.fn(),
        loading: false,
        refreshUser: vi.fn(),
      })

      render(
        <ProtectedRoute>
          <TestComponent />
        </ProtectedRoute>
      )

      await waitFor(() => {
        expect(screen.queryByRole('status')).not.toBeInTheDocument()
        expect(document.querySelector('.animate-spin')).not.toBeInTheDocument()
      })
    })
  })

  describe('unauthenticated state', () => {
    it('should not render children when not authenticated', () => {
      const pushSpy = vi.fn()

      vi.mocked(useAuth).mockReturnValue({
        isAuthenticated: false,
        user: null,
        login: vi.fn(),
        logout: vi.fn(),
        loading: false,
        refreshUser: vi.fn(),
      })

      vi.doMock('next/navigation', () => ({
        useRouter: () => ({
          push: pushSpy,
        }),
      }))

      render(
        <ProtectedRoute>
          <TestComponent />
        </ProtectedRoute>
      )

      expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument()
    })

    it('should redirect to login page when not authenticated', async () => {
      const pushSpy = vi.fn()

      vi.doMock('next/navigation', () => ({
        useRouter: () => ({
          push: pushSpy,
        }),
      }))

      mockUseAuth.mockReturnValue({
        isAuthenticated: false,
        user: null,
        login: vi.fn(),
        logout: vi.fn(),
        loading: false,
        refreshUser: vi.fn(),
      })

      render(
        <ProtectedRoute>
          <TestComponent />
        </ProtectedRoute>
      )

      await waitFor(() => {
        expect(pushSpy).toHaveBeenCalledWith('/login')
      })
    })
  })

  describe('multiple children', () => {
    it('should render all children when authenticated', async () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        user: { id: '1', email: 'test@example.com', plan_type: 'growth', is_verified: true },
        login: vi.fn(),
        logout: vi.fn(),
        loading: false,
        refreshUser: vi.fn(),
      })

      render(
        <ProtectedRoute>
          <div data-testid="child-1">Child 1</div>
          <div data-testid="child-2">Child 2</div>
          <div data-testid="child-3">Child 3</div>
        </ProtectedRoute>
      )

      await waitFor(() => {
        expect(screen.getByTestId('child-1')).toBeInTheDocument()
        expect(screen.getByTestId('child-2')).toBeInTheDocument()
        expect(screen.getByTestId('child-3')).toBeInTheDocument()
      })
    })

    it('should not render any children when not authenticated', () => {
      mockUseAuth.mockReturnValue({
        isAuthenticated: false,
        user: null,
        login: vi.fn(),
        logout: vi.fn(),
        loading: false,
        refreshUser: vi.fn(),
      })

      render(
        <ProtectedRoute>
          <div data-testid="child-1">Child 1</div>
          <div data-testid="child-2">Child 2</div>
          <div data-testid="child-3">Child 3</div>
        </ProtectedRoute>
      )

      expect(screen.queryByTestId('child-1')).not.toBeInTheDocument()
      expect(screen.queryByTestId('child-2')).not.toBeInTheDocument()
      expect(screen.queryByTestId('child-3')).not.toBeInTheDocument()
    })
  })

  describe('state transitions', () => {
    it('should show loading then render content when authentication completes', async () => {
      // Start with loading state
      mockUseAuth.mockReturnValue({
        isAuthenticated: false,
        user: null,
        login: vi.fn(),
        logout: vi.fn(),
        loading: true,
        refreshUser: vi.fn(),
      })

      const { rerender } = render(
        <ProtectedRoute>
          <TestComponent />
        </ProtectedRoute>
      )

      // Should show loading initially
      expect(document.querySelector('.animate-spin')).toBeInTheDocument()
      expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument()

      // Update to authenticated state
      mockUseAuth.mockReturnValue({
        isAuthenticated: true,
        user: { id: '1', email: 'test@example.com', plan_type: 'growth', is_verified: true },
        login: vi.fn(),
        logout: vi.fn(),
        loading: false,
        refreshUser: vi.fn(),
      })

      rerender(
        <ProtectedRoute>
          <TestComponent />
        </ProtectedRoute>
      )

      await waitFor(() => {
        expect(screen.getByTestId('protected-content')).toBeInTheDocument()
        expect(document.querySelector('.animate-spin')).not.toBeInTheDocument()
      })
    })

    it('should show loading then redirect when authentication fails', async () => {
      const pushSpy = vi.fn()

      // Start with loading state
      mockUseAuth.mockReturnValue({
        isAuthenticated: false,
        user: null,
        login: vi.fn(),
        logout: vi.fn(),
        loading: true,
        refreshUser: vi.fn(),
      })

      const { rerender } = render(
        <ProtectedRoute>
          <TestComponent />
        </ProtectedRoute>
      )

      // Should show loading initially
      expect(document.querySelector('.animate-spin')).toBeInTheDocument()

      // Update to unauthenticated state
      mockUseAuth.mockReturnValue({
        isAuthenticated: false,
        user: null,
        login: vi.fn(),
        logout: vi.fn(),
        loading: false,
        refreshUser: vi.fn(),
      })

      rerender(
        <ProtectedRoute>
          <TestComponent />
        </ProtectedRoute>
      )

      await waitFor(() => {
        expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument()
        expect(pushSpy).toHaveBeenCalledWith('/login')
      })
    })
  })
})
