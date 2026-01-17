import { describe, it, expect } from 'vitest'
import { render, screen } from '../../utils/test-utils'
import { EventTimeline, Event } from '@/components/competitors/EventTimeline'

const mockEvents: Event[] = [
  {
    id: '1',
    competitor_id: 'comp1',
    event_type: 'price',
    description: 'Competitor lowered their pricing by 20%',
    score: 5,
    timestamp: '2025-01-15T10:30:00Z',
  },
  {
    id: '2',
    competitor_id: 'comp1',
    event_type: 'feature',
    description: 'New AI-powered analytics feature launched',
    score: 6,
    timestamp: '2025-01-14T14:20:00Z',
  },
  {
    id: '3',
    competitor_id: 'comp1',
    event_type: 'health',
    description: 'Company showing strong growth indicators',
    score: 4,
    timestamp: '2025-01-13T09:15:00Z',
  },
  {
    id: '4',
    competitor_id: 'comp1',
    event_type: 'new_entrant',
    description: 'New competitor entering the market with aggressive pricing',
    score: 8,
    timestamp: '2025-01-12T16:45:00Z',
  },
]

describe('EventTimeline', () => {
  describe('loading state', () => {
    it('should render skeleton loaders while loading', () => {
      render(<EventTimeline events={[]} loading={true} />)

      const skeletons = document.querySelectorAll('.animate-pulse')
      expect(skeletons.length).toBeGreaterThan(0)
    })

    it('should render 3 skeleton items', () => {
      render(<EventTimeline events={[]} loading={true} />)

      const skeletons = document.querySelectorAll('.h-4.w-1\\/4.bg-gray-200')
      expect(skeletons.length).toBe(3)
    })

    it('should not show events while loading', () => {
      render(<EventTimeline events={mockEvents} loading={true} />)

      expect(screen.queryByText('Competitor lowered their pricing')).not.toBeInTheDocument()
    })
  })

  describe('empty state', () => {
    it('should show empty message when no events', () => {
      render(<EventTimeline events={[]} loading={false} />)

      expect(screen.getByText('No recent activity detected.')).toBeInTheDocument()
    })

    it('should not show skeleton loaders when not loading', () => {
      render(<EventTimeline events={[]} loading={false} />)

      const skeletons = document.querySelectorAll('.animate-pulse')
      expect(skeletons.length).toBe(0)
    })
  })

  describe('rendering events', () => {
    it('should render all events', () => {
      render(<EventTimeline events={mockEvents} loading={false} />)

      expect(screen.getByText('Competitor lowered their pricing by 20%')).toBeInTheDocument()
      expect(screen.getByText('New AI-powered analytics feature launched')).toBeInTheDocument()
      expect(screen.getByText('Company showing strong growth indicators')).toBeInTheDocument()
    })

    it('should render event types', () => {
      render(<EventTimeline events={mockEvents} loading={false} />)

      expect(screen.getByText('price')).toBeInTheDocument()
      expect(screen.getByText('feature')).toBeInTheDocument()
      expect(screen.getByText('health')).toBeInTheDocument()
      expect(screen.getByText('new_entrant')).toBeInTheDocument()
    })

    it('should render event descriptions', () => {
      render(<EventTimeline events={mockEvents} loading={false} />)

      const descriptions = screen.getAllByText(/competitor|new ai-powered|company showing|new competitor/i)
      expect(descriptions.length).toBeGreaterThan(0)
    })
  })

  describe('breakthrough events', () => {
    it('should highlight breakthrough events (score > 7)', () => {
      render(<EventTimeline events={mockEvents} loading={false} />)

      expect(screen.getByText('Breakthrough')).toBeInTheDocument()
    })

    it('should apply red styling to breakthrough events', () => {
      const { container } = render(<EventTimeline events={mockEvents} loading={false} />)

      const breakthroughCards = container.querySelectorAll('.bg-red-50')
      expect(breakthroughCards.length).toBeGreaterThan(0)
    })

    it('should show alert icon for breakthrough events', () => {
      const { container } = render(<EventTimeline events={mockEvents} loading={false} />)

      const alertIcons = container.querySelectorAll('.lucide-alert-triangle')
      expect(alertIcons.length).toBeGreaterThan(0)
    })

    it('should not show breakthrough for low scores', () => {
      const lowScoreEvents: Event[] = [
        {
          id: '1',
          competitor_id: 'comp1',
          event_type: 'price',
          description: 'Minor price adjustment',
          score: 3,
          timestamp: '2025-01-15T10:30:00Z',
        },
      ]

      render(<EventTimeline events={lowScoreEvents} loading={false} />)

      expect(screen.queryByText('Breakthrough')).not.toBeInTheDocument()
    })
  })

  describe('event type styling', () => {
    it('should apply green color for price events', () => {
      render(<EventTimeline events={[mockEvents[0]]} loading={false} />)

      const priceBadge = screen.getByText('price')
      expect(priceBadge).toHaveClass('text-green-600')
    })

    it('should apply blue color for feature events', () => {
      render(<EventTimeline events={[mockEvents[1]]} loading={false} />)

      const featureBadge = screen.getByText('feature')
      expect(featureBadge).toHaveClass('text-blue-600')
    })

    it('should apply purple color for health events', () => {
      render(<EventTimeline events={[mockEvents[2]]} loading={false} />)

      const healthBadge = screen.getByText('health')
      expect(healthBadge).toHaveClass('text-purple-600')
    })

    it('should apply red color for high score events regardless of type', () => {
      render(<EventTimeline events={[mockEvents[3]]} loading={false} />)

      const newEntrantBadge = screen.getByText('new_entrant')
      expect(newEntrantBadge).toHaveClass('text-red-600')
    })
  })

  describe('date formatting', () => {
    it('should format dates correctly', () => {
      render(<EventTimeline events={mockEvents} loading={false} />)

      const dates = screen.getAllByText(/\d{1,2}\/\d{1,2}\/\d{4}/)
      expect(dates.length).toBeGreaterThan(0)
    })
  })

  describe('timeline structure', () => {
    it('should render timeline border', () => {
      const { container } = render(<EventTimeline events={mockEvents} loading={false} />)

      const border = container.querySelector('.border-l-2')
      expect(border).toBeInTheDocument()
    })

    it('should render event markers', () => {
      const { container } = render(<EventTimeline events={mockEvents} loading={false} />)

      const markers = container.querySelectorAll('.rounded-full')
      expect(markers.length).toBeGreaterThan(0)
    })
  })

  describe('event cards', () => {
    it('should render event cards with proper styling', () => {
      const { container } = render(<EventTimeline events={mockEvents} loading={false} />)

      const cards = container.querySelectorAll('.rounded-lg.border')
      expect(cards.length).toBe(mockEvents.length)
    })

    it('should have proper spacing between events', () => {
      const { container } = render(<EventTimeline events={mockEvents} loading={false} />)

      const timeline = container.querySelector('.space-y-8')
      expect(timeline).toBeInTheDocument()
    })
  })
})
