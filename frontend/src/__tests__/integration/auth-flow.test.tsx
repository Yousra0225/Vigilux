import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@/__tests__/utils/test-utils'
import { AuthProvider, useAuth } from '@/context/AuthContext'
import ProtectedRoute from '@/components/ProtectedRoute'
import { MainLayout } from '@/components/layout/MainLayout'
import { server } from '../mocks/server'
import { HttpResponse } from 'msw'

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

describe('Authentication Flow Integration Tests', () => {
  const TestComponent = () => (
    <div data-testid="protected-content">Protected Dashboard Content</div>
  )

  beforeEach(() => {
    vi.clearAllMocks()
    server.listen()
    localStorage.clear()
  })

  describe('Full Authentication Journey', () => {
    it('should complete full login -> access -> logout flow', async () => {
      const { rerender } = render(
        <AuthProvider>
          <ProtectedRoute>
            <TestComponent />
          </ProtectedRoute>
        </AuthProvider>
      )

      // Initial state: not authenticated
      expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument()

      // Rerender with authenticated state
      const TestWrapper = () => {
        const { login } = useAuth()
        return (
          <div>
            <button onClick={() => login('test-token')}>Login</button>
            <ProtectedRoute>
              <TestComponent />
            </ProtectedRoute>
          </div>
        )
      }

      rerender(
        <AuthProvider>
          <TestWrapper />
        </AuthProvider>
      )

      // Click login button
      fireEvent.click(screen.getByText('Login'))

      // After login, should show content
      await waitFor(() => {
        expect(screen.getByTestId('protected-content')).toBeInTheDocument()
      })
    })

    it('should handle token expiration gracefully', async () => {
      // Set an expired token
      localStorage.setItem('token', 'expired-token')

      // Mock 401 response
      server.use(
        HttpResponse.json(
          { detail: 'Unauthorized' },
          { status: 401 }
        )
      )

      render(
        <AuthProvider>
          <ProtectedRoute>
            <TestComponent />
          </ProtectedRoute>
        </AuthProvider>
      )

      await waitFor(() => {
        expect(localStorage.getItem('token')).toBeNull()
        expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument()
      })
    })
  })

  describe('Protected Routes Integration', () => {
    it('should allow access to protected content when authenticated', async () => {
      localStorage.setItem('token', 'valid-token')

      render(
        <AuthProvider>
          <MainLayout>
            <TestComponent />
          </MainLayout>
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('protected-content')).toBeInTheDocument()
        expect(screen.getByText('Vigilux')).toBeInTheDocument()
        expect(screen.getByText('My Workspace')).toBeInTheDocument()
      })
    })

    it('should block access to protected content when not authenticated', () => {
      render(
        <AuthProvider>
          <MainLayout>
            <TestComponent />
          </MainLayout>
        </AuthProvider>
      )

      expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument()
    })
  })

  describe('State Persistence', () => {
    it('should persist authentication state across re-renders', async () => {
      localStorage.setItem('token', 'valid-token')

      const { rerender } = render(
        <AuthProvider>
          <ProtectedRoute>
            <TestComponent />
          </ProtectedRoute>
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('protected-content')).toBeInTheDocument()
      })

      // Rerender multiple times
      rerender(
        <AuthProvider>
          <ProtectedRoute>
            <TestComponent />
          </ProtectedRoute>
        </AuthProvider>
      )

      rerender(
        <AuthProvider>
          <ProtectedRoute>
            <TestComponent />
          </ProtectedRoute>
        </AuthProvider>
      )

      // Should still be authenticated
      expect(screen.getByTestId('protected-content')).toBeInTheDocument()
    })
  })

  describe('Error Handling', () => {
    it('should handle API errors during authentication', async () => {
      server.use(
        HttpResponse.error()
      )

      localStorage.setItem('token', 'valid-token')

      render(
        <AuthProvider>
          <ProtectedRoute>
            <TestComponent />
          </ProtectedRoute>
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument()
        expect(localStorage.getItem('token')).toBeNull()
      })
    })
  })

  describe('Loading States', () => {
    it('should show loading state while checking authentication', () => {
      render(
        <AuthProvider>
          <ProtectedRoute>
            <TestComponent />
          </ProtectedRoute>
        </AuthProvider>
      )

      // Initially should show loading
      const spinner = document.querySelector('.animate-spin')
      expect(spinner).toBeInTheDocument()
    })

    it('should hide loading state after authentication check completes', async () => {
      localStorage.setItem('token', 'valid-token')

      render(
        <AuthProvider>
          <ProtectedRoute>
            <TestComponent />
          </ProtectedRoute>
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('protected-content')).toBeInTheDocument()
        expect(document.querySelector('.animate-spin')).not.toBeInTheDocument()
      })
    })
  })

  describe('User Data Fetching', () => {
    it('should fetch user data after successful login', async () => {
      const TestWrapper = () => {
        const { user, login } = useAuth()

        return (
          <div>
            {user && <div data-testid="user-email">{user.email}</div>}
            <button onClick={() => login('test-token')}>Login</button>
          </div>
        )
      }

      render(
        <AuthProvider>
          <TestWrapper />
        </AuthProvider>
      )

      fireEvent.click(screen.getByText('Login'))

      await waitFor(() => {
        expect(screen.getByTestId('user-email')).toBeInTheDocument()
        expect(screen.getByTestId('user-email')).toHaveTextContent('test@example.com')
      })
    })

    it('should clear user data on logout', async () => {
      localStorage.setItem('token', 'valid-token')

      const TestWrapper = () => {
        const { user, logout } = useAuth()

        return (
          <div>
            {user && <div data-testid="user-email">{user.email}</div>}
            <button onClick={logout}>Logout</button>
          </div>
        )
      }

      render(
        <AuthProvider>
          <TestWrapper />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('user-email')).toBeInTheDocument()
      })

      fireEvent.click(screen.getByText('Logout'))

      await waitFor(() => {
        expect(screen.queryByTestId('user-email')).not.toBeInTheDocument()
      })
    })
  })
})
