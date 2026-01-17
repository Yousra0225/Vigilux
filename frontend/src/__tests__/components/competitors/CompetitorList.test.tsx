import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '../../utils/test-utils'
import { CompetitorList, Competitor } from '@/components/competitors/CompetitorList'

const mockCompetitors: Competitor[] = [
  {
    id: '1',
    name: 'TechCorp Inc',
    url: 'https://techcorp.com',
    score: 85,
    tracking_status: 'active',
  },
  {
    id: '2',
    name: 'InnovateTech Ltd',
    url: 'https://innovatetech.com',
    score: 72,
    tracking_status: 'active',
  },
  {
    id: '3',
    name: 'DataFlow Systems',
    score: 91,
    tracking_status: 'active',
  },
]

describe('CompetitorList', () => {
  describe('loading state', () => {
    it('should render skeleton loaders while loading', () => {
      render(
        <CompetitorList
          competitors={[]}
          selectedId={null}
          onSelect={vi.fn()}
          loading={true}
        />
      )

      const skeletons = document.querySelectorAll('.animate-pulse')
      expect(skeletons.length).toBeGreaterThan(0)
    })

    it('should render 3 skeleton items', () => {
      render(
        <CompetitorList
          competitors={[]}
          selectedId={null}
          onSelect={vi.fn()}
          loading={true}
        />
      )

      const skeletons = document.querySelectorAll('h-16.bg-gray-100.dark\\:bg-gray-800')
      expect(skeletons.length).toBe(3)
    })

    it('should not show competitors while loading', () => {
      render(
        <CompetitorList
          competitors={mockCompetitors}
          selectedId={null}
          onSelect={vi.fn()}
          loading={true}
        />
      )

      expect(screen.queryByText('TechCorp Inc')).not.toBeInTheDocument()
    })
  })

  describe('empty state', () => {
    it('should show empty message when no competitors', () => {
      render(
        <CompetitorList
          competitors={[]}
          selectedId={null}
          onSelect={vi.fn()}
          loading={false}
        />
      )

      expect(screen.getByText('No competitors found.')).toBeInTheDocument()
    })

    it('should not show skeleton loaders when not loading', () => {
      render(
        <CompetitorList
          competitors={[]}
          selectedId={null}
          onSelect={vi.fn()}
          loading={false}
        />
      )

      const skeletons = document.querySelectorAll('.animate-pulse')
      expect(skeletons.length).toBe(0)
    })
  })

  describe('rendering competitors', () => {
    it('should render all competitors', () => {
      render(
        <CompetitorList
          competitors={mockCompetitors}
          selectedId={null}
          onSelect={vi.fn()}
          loading={false}
        />
      )

      expect(screen.getByText('TechCorp Inc')).toBeInTheDocument()
      expect(screen.getByText('InnovateTech Ltd')).toBeInTheDocument()
      expect(screen.getByText('DataFlow Systems')).toBeInTheDocument()
    })

    it('should render competitor scores', () => {
      render(
        <CompetitorList
          competitors={mockCompetitors}
          selectedId={null}
          onSelect={vi.fn()}
          loading={false}
        />
      )

      expect(screen.getByText('85')).toBeInTheDocument()
      expect(screen.getByText('72')).toBeInTheDocument()
      expect(screen.getByText('91')).toBeInTheDocument()
    })

    it('should render URLs when present', () => {
      render(
        <CompetitorList
          competitors={mockCompetitors}
          selectedId={null}
          onSelect={vi.fn()}
          loading={false}
        />
      )

      expect(screen.getByText('techcorp.com')).toBeInTheDocument()
      expect(screen.getByText('innovatetech.com')).toBeInTheDocument()
    })

    it('should not render URL when not present', () => {
      const competitorsWithoutUrl: Competitor[] = [
        {
          id: '1',
          name: 'TechCorp Inc',
          score: 85,
          tracking_status: 'active',
        },
      ]

      render(
        <CompetitorList
          competitors={competitorsWithoutUrl}
          selectedId={null}
          onSelect={vi.fn()}
          loading={false}
        />
      )

      expect(screen.queryByText('techcorp.com')).not.toBeInTheDocument()
    })
  })

  describe('selection', () => {
    it('should call onSelect when competitor is clicked', () => {
      const onSelect = vi.fn()

      render(
        <CompetitorList
          competitors={mockCompetitors}
          selectedId={null}
          onSelect={onSelect}
          loading={false}
        />
      )

      fireEvent.click(screen.getByText('TechCorp Inc'))
      expect(onSelect).toHaveBeenCalledWith('1')
    })

    it('should apply selected styles to selected competitor', () => {
      const { container } = render(
        <CompetitorList
          competitors={mockCompetitors}
          selectedId='1'
          onSelect={vi.fn()}
          loading={false}
        />
      )

      const selectedCard = screen.getByText('TechCorp Inc').closest('[class*="cursor-pointer"]')
      expect(selectedCard).toHaveClass('bg-blue-50')
    })

    it('should not apply selected styles to unselected competitors', () => {
      render(
        <CompetitorList
          competitors={mockCompetitors}
          selectedId='1'
          onSelect={vi.fn()}
          loading={false}
        />
      )

      const unselectedCard = screen.getByText('InnovateTech Ltd').closest('[class*="cursor-pointer"]')
      expect(unselectedCard).not.toHaveClass('bg-blue-50')
    })
  })

  describe('score styling', () => {
    it('should apply red styling for high scores (> 70)', () => {
      render(
        <CompetitorList
          competitors={[mockCompetitors[0]]}
          selectedId={null}
          onSelect={vi.fn()}
          loading={false}
        />
      )

      const scoreBadge = screen.getByText('85')
      expect(scoreBadge).toHaveClass('bg-red-100', 'text-red-700')
    })

    it('should apply yellow styling for medium scores (> 40)', () => {
      render(
        <CompetitorList
          competitors={[mockCompetitors[1]]}
          selectedId={null}
          onSelect={vi.fn()}
          loading={false}
        />
      )

      const scoreBadge = screen.getByText('72')
      expect(scoreBadge).toHaveClass('bg-yellow-100', 'text-yellow-700')
    })

    it('should apply green styling for low scores (<= 40)', () => {
      const lowScoreCompetitor: Competitor = {
        id: '1',
        name: 'Low Score Inc',
        score: 35,
        tracking_status: 'active',
      }

      render(
        <CompetitorList
          competitors={[lowScoreCompetitor]}
          selectedId={null}
          onSelect={vi.fn()}
          loading={false}
        />
      )

      const scoreBadge = screen.getByText('35')
      expect(scoreBadge).toHaveClass('bg-green-100', 'text-green-700')
    })
  })

  describe('external links', () => {
    it('should have correct link attributes', () => {
      render(
        <CompetitorList
          competitors={mockCompetitors}
          selectedId={null}
          onSelect={vi.fn()}
          loading={false}
        />
      )

      const link = screen.getByText('techcorp.com').closest('a')
      expect(link).toHaveAttribute('href', 'https://techcorp.com')
      expect(link).toHaveAttribute('target', '_blank')
      expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    })

    it('should not trigger onSelect when clicking URL link', () => {
      const onSelect = vi.fn()

      render(
        <CompetitorList
          competitors={mockCompetitors}
          selectedId={null}
          onSelect={onSelect}
          loading={false}
        />
      )

      const link = screen.getByText('techcorp.com').closest('a')
      fireEvent.click(link!, { stopPropagation: () => {} })

      expect(onSelect).not.toHaveBeenCalled()
    })
  })
})
