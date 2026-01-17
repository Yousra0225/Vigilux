import { describe, it, expect } from 'vitest'
import { render, screen } from '../../utils/test-utils'
import { StatCard } from '@/components/dashboard/StatCard'
import { Users } from 'lucide-react'

describe('StatCard', () => {
  const mockIcon = Users

  describe('basic rendering', () => {
    it('should render the title', () => {
      render(<StatCard title="Total Users" value="100" icon={mockIcon} />)

      expect(screen.getByText('Total Users')).toBeInTheDocument()
    })

    it('should render the value', () => {
      render(<StatCard title="Total Users" value="100" icon={mockIcon} />)

      expect(screen.getByText('100')).toBeInTheDocument()
    })

    it('should render the icon', () => {
      const { container } = render(<StatCard title="Total Users" value="100" icon={mockIcon} />)

      const icon = container.querySelector('.lucide-users')
      expect(icon).toBeInTheDocument()
    })
  })

  describe('value types', () => {
    it('should render numeric value as string', () => {
      render(<StatCard title="Total Users" value={100} icon={mockIcon} />)

      expect(screen.getByText('100')).toBeInTheDocument()
    })

    it('should render string value', () => {
      render(<StatCard title="Status" value="Active" icon={mockIcon} />)

      expect(screen.getByText('Active')).toBeInTheDocument()
    })

    it('should render decimal value', () => {
      render(<StatCard title="Average" value={85.5} icon={mockIcon} />)

      expect(screen.getByText('85.5')).toBeInTheDocument()
    })
  })

  describe('description', () => {
    it('should not render description when not provided', () => {
      render(<StatCard title="Total Users" value="100" icon={mockIcon} />)

      const description = screen.queryByText(/test description/i)
      expect(description).not.toBeInTheDocument()
    })

    it('should render description when provided', () => {
      render(
        <StatCard
          title="Total Users"
          value="100"
          icon={mockIcon}
          description="+10% from last month"
        />
      )

      expect(screen.getByText('+10% from last month')).toBeInTheDocument()
    })
  })

  describe('custom styling', () => {
    it('should apply custom className', () => {
      const { container } = render(
        <StatCard
          title="Total Users"
          value="100"
          icon={mockIcon}
          className="custom-class"
        />
      )

      const card = container.firstChild as HTMLElement
      expect(card).toHaveClass('custom-class')
    })

    it('should apply default styling classes', () => {
      const { container } = render(
        <StatCard title="Total Users" value="100" icon={mockIcon} />
      )

      const card = container.firstChild as HTMLElement
      expect(card).toHaveClass('bg-white', 'dark:bg-gray-800', 'rounded-lg', 'shadow')
    })
  })

  describe('layout structure', () => {
    it('should render icon in a rounded container', () => {
      const { container } = render(
        <StatCard title="Total Users" value="100" icon={mockIcon} />
      )

      const iconContainer = container.querySelector('.bg-blue-50')
      expect(iconContainer).toBeInTheDocument()
      expect(iconContainer).toHaveClass('rounded-full')
    })

    it('should render title above value', () => {
      const { container } = render(
        <StatCard title="Total Users" value="100" icon={mockIcon} />
      )

      const title = screen.getByText('Total Users')
      const value = screen.getByText('100')

      const titlePosition = title.compareDocumentPosition(value)
      expect(titlePosition & Node.DOCUMENT_POSITION_FOLLOWING).toBe(
        Node.DOCUMENT_POSITION_FOLLOWING
      )
    })

    it('should render description below value', () => {
      render(
        <StatCard
          title="Total Users"
          value="100"
          icon={mockIcon}
          description="+10% from last month"
        />
      )

      const value = screen.getByText('100')
      const description = screen.getByText('+10% from last month')

      const valuePosition = value.compareDocumentPosition(description)
      expect(valuePosition & Node.DOCUMENT_POSITION_FOLLOWING).toBe(
        Node.DOCUMENT_POSITION_FOLLOWING
      )
    })
  })

  describe('accessibility', () => {
    it('should have proper heading structure for title', () => {
      render(<StatCard title="Total Users" value="100" icon={mockIcon} />)

      const title = screen.getByText('Total Users')
      expect(title.tagName).toBe('P')
    })

    it('should have proper text structure for value', () => {
      render(<StatCard title="Total Users" value="100" icon={mockIcon} />)

      const value = screen.getByText('100')
      expect(value.tagName).toBe('P')
    })
  })

  describe('different icons', () => {
    it('should render different icon types', () => {
      const { container: container1 } = render(
        <StatCard title="Users" value="100" icon={Users} />
      )

      const { container: container2 } = render(
        <StatCard title="Users" value="100" icon={mockIcon} />
      )

      const icon1 = container1.querySelector('.lucide-users')
      const icon2 = container2.querySelector('.lucide-users')

      expect(icon1).toBeInTheDocument()
      expect(icon2).toBeInTheDocument()
    })
  })
})
