import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@/__tests__/utils/test-utils'
import { MainLayout } from '@/components/layout/MainLayout'
import { useAuth } from '@/context/AuthContext'

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}))

vi.mock('@/context/AuthContext', () => ({
  useAuth: vi.fn(),
}))

describe('MainLayout', () => {
  beforeEach(() => {
    vi.clearAllMocks()

    vi.mocked(useAuth).mockReturnValue({
      isAuthenticated: true,
      user: { id: '1', email: 'test@example.com', plan_type: 'growth', is_verified: true },
      login: vi.fn(),
      logout: vi.fn(),
      loading: false,
      refreshUser: vi.fn(),
    })
  })

  describe('when authenticated', () => {
    it('should render sidebar', () => {
      render(
        <MainLayout>
          <div data-testid="test-content">Test Content</div>
        </MainLayout>
      )

      expect(screen.getByText('Vigilux')).toBeInTheDocument()
    })

    it('should render header', () => {
      render(
        <MainLayout>
          <div data-testid="test-content">Test Content</div>
        </MainLayout>
      )

      expect(screen.getByText('My Workspace')).toBeInTheDocument()
    })

    it('should render children content', () => {
      render(
        <MainLayout>
          <div data-testid="test-content">Test Content</div>
        </MainLayout>
      )

      expect(screen.getByTestId('test-content')).toBeInTheDocument()
      expect(screen.getByText('Test Content')).toBeInTheDocument()
    })

    it('should apply correct layout structure', () => {
      const { container } = render(
        <MainLayout>
          <div data-testid="test-content">Test Content</div>
        </MainLayout>
      )

      const mainContainer = container.querySelector('.flex.min-h-screen')
      expect(mainContainer).toBeInTheDocument()

      const sidebar = container.querySelector('aside')
      expect(sidebar).toBeInTheDocument()

      const header = container.querySelector('header')
      expect(header).toBeInTheDocument()

      const main = container.querySelector('main')
      expect(main).toBeInTheDocument()
    })
  })

  describe('when not authenticated', () => {
    beforeEach(() => {
      vi.mocked(useAuth).mockReturnValue({
        isAuthenticated: false,
        user: null,
        login: vi.fn(),
        logout: vi.fn(),
        loading: false,
        refreshUser: vi.fn(),
      })
    })

    it('should not render layout content', () => {
      const { container } = render(
        <MainLayout>
          <div data-testid="test-content">Test Content</div>
        </MainLayout>
      )

      expect(screen.queryByTestId('test-content')).not.toBeInTheDocument()
    })
  })

  describe('when loading', () => {
    beforeEach(() => {
      vi.mocked(useAuth).mockReturnValue({
        isAuthenticated: false,
        user: null,
        login: vi.fn(),
        logout: vi.fn(),
        loading: true,
        refreshUser: vi.fn(),
      })
    })

    it('should show loading state', () => {
      render(
        <MainLayout>
          <div data-testid="test-content">Test Content</div>
        </MainLayout>
      )

      expect(screen.queryByTestId('test-content')).not.toBeInTheDocument()
    })
  })

  describe('multiple children', () => {
    it('should render all children', () => {
      render(
        <MainLayout>
          <div data-testid="child-1">Child 1</div>
          <div data-testid="child-2">Child 2</div>
          <div data-testid="child-3">Child 3</div>
        </MainLayout>
      )

      expect(screen.getByTestId('child-1')).toBeInTheDocument()
      expect(screen.getByTestId('child-2')).toBeInTheDocument()
      expect(screen.getByTestId('child-3')).toBeInTheDocument()
    })
  })

  describe('responsive behavior', () => {
    it('should apply responsive classes', () => {
      const { container } = render(
        <MainLayout>
          <div data-testid="test-content">Test Content</div>
        </MainLayout>
      )

      const main = container.querySelector('main')
      expect(main).toHaveClass('p-4', 'sm:p-6', 'lg:p-8')
    })
  })
})
