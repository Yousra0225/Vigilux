import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { AuthProvider, useAuth } from '@/context/AuthContext'
import axios from 'axios'
import { server } from '../mocks/server'
import { HttpResponse } from 'msw'
import { toast } from 'sonner'

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

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <AuthProvider>{children}</AuthProvider>
)

describe('AuthContext', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()
    server.listen()
    vi.clearAllMocks()
  })

  afterEach(() => {
    server.resetHandlers()
  })

  describe('initial state', () => {
    it('should start with loading state and no user when no token', async () => {
      const { result } = renderHook(() => useAuth(), { wrapper })

      expect(result.current.loading).toBe(true)
      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
    })

    it('should fetch user when token exists in localStorage', async () => {
      localStorage.setItem('token', 'valid-token')

      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.isAuthenticated).toBe(true)
      expect(result.current.user).toEqual({
        id: '1',
        email: 'test@example.com',
        full_name: 'Test User',
      })
    })
  })

  describe('login', () => {
    it('should store token, fetch user, and redirect', async () => {
      const { result } = renderHook(() => useAuth(), { wrapper })

      await act(async () => {
        await result.current.login('valid-token')
      })

      expect(localStorage.getItem('token')).toBe('valid-token')

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.isAuthenticated).toBe(true)
      expect(result.current.user).toEqual({
        id: '1',
        email: 'test@example.com',
        full_name: 'Test User',
      })
      expect(toast.success).toHaveBeenCalledWith('Successfully logged in')
    })

    it('should persist authentication across re-renders', async () => {
      const { result, rerender } = renderHook(() => useAuth(), { wrapper })

      await act(async () => {
        await result.current.login('valid-token')
      })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      // Rerender to check persistence
      rerender()

      expect(result.current.isAuthenticated).toBe(true)
      expect(result.current.user).toEqual({
        id: '1',
        email: 'test@example.com',
        full_name: 'Test User',
      })
    })
  })

  describe('logout', () => {
    it('should clear token, user state, and redirect', async () => {
      localStorage.setItem('token', 'valid-token')

      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(true)
      })

      act(() => {
        result.current.logout()
      })

      expect(localStorage.getItem('token')).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.user).toBeNull()
      expect(toast.info).toHaveBeenCalledWith('Logged out')
    })
  })

  describe('refreshUser', () => {
    it('should fetch updated user data', async () => {
      localStorage.setItem('token', 'valid-token')

      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.user).toEqual({
        id: '1',
        email: 'test@example.com',
        full_name: 'Test User',
      })

      // Refresh user
      await act(async () => {
        await result.current.refreshUser()
      })

      expect(result.current.user).toEqual({
        id: '1',
        email: 'test@example.com',
        full_name: 'Test User',
      })
    })

    it('should handle errors when fetching user', async () => {
      server.use(
        HttpResponse.json(
          { detail: 'Unauthorized' },
          { status: 401 }
        )
      )

      localStorage.setItem('token', 'invalid-token')

      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.user).toBeNull()
      expect(localStorage.getItem('token')).toBeNull()
    })
  })

  describe('useAuth hook', () => {
    it('should throw error when used outside AuthProvider', () => {
      // Suppress console.error for this test
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      expect(() => {
        renderHook(() => useAuth())
      }).toThrow('useAuth must be used within an AuthProvider')

      consoleSpy.mockRestore()
    })

    it('should provide auth context when used within AuthProvider', async () => {
      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current).toHaveProperty('isAuthenticated')
      expect(result.current).toHaveProperty('user')
      expect(result.current).toHaveProperty('login')
      expect(result.current).toHaveProperty('logout')
      expect(result.current).toHaveProperty('loading')
      expect(result.current).toHaveProperty('refreshUser')
    })
  })

  describe('error handling', () => {
    it('should handle 401 unauthorized errors', async () => {
      server.use(
        HttpResponse.json(
          { detail: 'Unauthorized' },
          { status: 401 }
        )
      )

      localStorage.setItem('token', 'expired-token')

      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.user).toBeNull()
      expect(localStorage.getItem('token')).toBeNull()
    })

    it('should handle network errors gracefully', async () => {
      server.use(
        HttpResponse.error()
      )

      localStorage.setItem('token', 'valid-token')

      const { result } = renderHook(() => useAuth(), { wrapper })

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.user).toBeNull()
    })
  })
})
