import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@/__tests__/utils/test-utils'
import { Sidebar } from '@/components/layout/Sidebar'

vi.mock('next/navigation', () => ({
  usePathname: () => '/dashboard',
}))

describe('Sidebar', () => {
  describe('rendering', () => {
    it('should render the sidebar with all navigation items', () => {
      render(<Sidebar />)

      expect(screen.getByText('Dashboard')).toBeInTheDocument()
      expect(screen.getByText('Competitors')).toBeInTheDocument()
      expect(screen.getByText('Radar')).toBeInTheDocument()
      expect(screen.getByText('Settings')).toBeInTheDocument()
    })

    it('should render the Vigilux logo', () => {
      render(<Sidebar />)
      expect(screen.getByText('Vigilux')).toBeInTheDocument()
    })

    it('should render mobile menu button', () => {
      render(<Sidebar />)

      const menuButton = screen.getByRole('button')
      expect(menuButton).toBeInTheDocument()
    })
  })

  describe('mobile menu', () => {
    it('should open sidebar when mobile menu button is clicked', async () => {
      render(<Sidebar />)

      const menuButton = screen.getByRole('button')
      fireEvent.click(menuButton)

      await waitFor(() => {
        const sidebar = document.querySelector('aside')
        expect(sidebar).toHaveClass('translate-x-0')
      })
    })

    it('should close sidebar when X button is clicked', async () => {
      render(<Sidebar />)

      // Open the sidebar
      const menuButton = screen.getByRole('button')
      fireEvent.click(menuButton)

      await waitFor(() => {
        const sidebar = document.querySelector('aside')
        expect(sidebar).toHaveClass('translate-x-0')
      })

      // Click the X button
      fireEvent.click(menuButton)

      await waitFor(() => {
        const sidebar = document.querySelector('aside')
        expect(sidebar).toHaveClass('-translate-x-full')
      })
    })

    it('should show overlay when sidebar is open on mobile', async () => {
      render(<Sidebar />)

      const menuButton = screen.getByRole('button')
      fireEvent.click(menuButton)

      await waitFor(() => {
        const overlay = document.querySelector('.bg-black\\/50')
        expect(overlay).toBeInTheDocument()
      })
    })

    it('should close sidebar when overlay is clicked', async () => {
      render(<Sidebar />)

      // Open the sidebar
      const menuButton = screen.getByRole('button')
      fireEvent.click(menuButton)

      await waitFor(() => {
        const overlay = document.querySelector('.bg-black\\/50')
        expect(overlay).toBeInTheDocument()
      })

      // Click the overlay
      const overlay = document.querySelector('.bg-black\\/50')
      fireEvent.click(overlay!)

      await waitFor(() => {
        const sidebar = document.querySelector('aside')
        expect(sidebar).toHaveClass('-translate-x-full')
      })
    })
  })

  describe('navigation items', () => {
    it('should render all navigation links with correct icons', () => {
      render(<Sidebar />)

      const dashboardLink = screen.getByText('Dashboard').closest('a')
      const competitorsLink = screen.getByText('Competitors').closest('a')
      const radarLink = screen.getByText('Radar').closest('a')
      const settingsLink = screen.getByText('Settings').closest('a')

      expect(dashboardLink?.getAttribute('href')).toBe('/dashboard')
      expect(competitorsLink?.getAttribute('href')).toBe('/dashboard/competitors')
      expect(radarLink?.getAttribute('href')).toBe('/dashboard/radar')
      expect(settingsLink?.getAttribute('href')).toBe('/dashboard/settings')
    })

    it('should highlight active navigation item', () => {
      render(<Sidebar />)

      const dashboardLink = screen.getByText('Dashboard').closest('a')
      expect(dashboardLink).toHaveClass('bg-gray-100')
    })

    it('should not highlight inactive navigation items', () => {
      render(<Sidebar />)

      const competitorsLink = screen.getByText('Competitors').closest('a')
      expect(competitorsLink).not.toHaveClass('bg-gray-100')
    })

    it('should close mobile sidebar when navigation item is clicked', async () => {
      render(<Sidebar />)

      // Open the sidebar
      const menuButton = screen.getByRole('button')
      fireEvent.click(menuButton)

      await waitFor(() => {
        const sidebar = document.querySelector('aside')
        expect(sidebar).toHaveClass('translate-x-0')
      })

      // Click on a navigation item
      const dashboardLink = screen.getByText('Dashboard').closest('a')
      fireEvent.click(dashboardLink!)

      await waitFor(() => {
        const sidebar = document.querySelector('aside')
        expect(sidebar).toHaveClass('-translate-x-full')
      })
    })
  })

  describe('responsive behavior', () => {
    it('should apply correct classes for desktop view', () => {
      render(<Sidebar />)

      const sidebar = document.querySelector('aside')
      expect(sidebar).toHaveClass('lg:translate-x-0')
      expect(sidebar).toHaveClass('lg:static')
    })

    it('should apply correct classes for mobile view', () => {
      render(<Sidebar />)

      const sidebar = document.querySelector('aside')
      expect(sidebar).toHaveClass('-translate-x-full')
      expect(sidebar).toHaveClass('fixed')
    })
  })
})
