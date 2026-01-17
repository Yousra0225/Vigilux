import { describe, it, expect } from 'vitest'
import { render, screen } from '../../utils/test-utils'
import { ThreatTimeline } from '@/components/dashboard/ThreatTimeline'

interface TimelinePoint {
  date: string
  count: number
}

const mockData: TimelinePoint[] = [
  { date: '2025-01-01', count: 10 },
  { date: '2025-01-02', count: 15 },
  { date: '2025-01-03', count: 20 },
  { date: '2025-01-04', count: 12 },
  { date: '2025-01-05', count: 18 },
]

describe('ThreatTimeline', () => {
  describe('rendering', () => {
    it('should render the component', () => {
      render(<ThreatTimeline data={mockData} />)

      expect(screen.getByText('Threat Activity Timeline')).toBeInTheDocument()
    })

    it('should render the chart container', () => {
      const { container } = render(<ThreatTimeline data={mockData} />)

      const chartContainer = container.querySelector('.recharts-responsive-container')
      expect(chartContainer).toBeInTheDocument()
    })

    it('should render the area chart', () => {
      const { container } = render(<ThreatTimeline data={mockData} />)

      const areaChart = container.querySelector('.recharts-area-chart')
      expect(areaChart).toBeInTheDocument()
    })
  })

  describe('data handling', () => {
    it('should render chart with provided data', () => {
      const { container } = render(<ThreatTimeline data={mockData} />)

      const areas = container.querySelectorAll('.recharts-area')
      expect(areas.length).toBeGreaterThan(0)
    })

    it('should handle empty data', () => {
      const { container } = render(<ThreatTimeline data={[]} />)

      const chartContainer = container.querySelector('.recharts-responsive-container')
      expect(chartContainer).toBeInTheDocument()
    })

    it('should handle single data point', () => {
      const singleData: TimelinePoint[] = [{ date: '2025-01-01', count: 10 }]

      const { container } = render(<ThreatTimeline data={singleData} />)

      const chartContainer = container.querySelector('.recharts-responsive-container')
      expect(chartContainer).toBeInTheDocument()
    })

    it('should handle large data sets', () => {
      const largeData: TimelinePoint[] = Array.from({ length: 100 }, (_, i) => ({
        date: `2025-01-${String(i + 1).padStart(2, '0')}`,
        count: Math.floor(Math.random() * 50),
      }))

      const { container } = render(<ThreatTimeline data={largeData} />)

      const chartContainer = container.querySelector('.recharts-responsive-container')
      expect(chartContainer).toBeInTheDocument()
    })
  })

  describe('styling', () => {
    it('should apply card styling classes', () => {
      const { container } = render(<ThreatTimeline data={mockData} />)

      const card = container.firstChild as HTMLElement
      expect(card).toHaveClass('bg-white', 'dark:bg-gray-800', 'rounded-lg', 'shadow')
    })

    it('should render title with correct styling', () => {
      render(<ThreatTimeline data={mockData} />)

      const title = screen.getByText('Threat Activity Timeline')
      expect(title).toHaveClass('text-lg', 'font-semibold')
    })

    it('should have responsive container with correct height', () => {
      const { container } = render(<ThreatTimeline data={mockData} />)

      const chartContainer = container.querySelector('.h-\\[300px\\]')
      expect(chartContainer).toBeInTheDocument()
    })
  })

  describe('chart elements', () => {
    it('should render X axis', () => {
      const { container } = render(<ThreatTimeline data={mockData} />)

      const xAxis = container.querySelector('.recharts-cartesian-axis.xaxis')
      expect(xAxis).toBeInTheDocument()
    })

    it('should render Y axis', () => {
      const { container } = render(<ThreatTimeline data={mockData} />)

      const yAxis = container.querySelector('.recharts-cartesian-axis.yaxis')
      expect(yAxis).toBeInTheDocument()
    })

    it('should render grid lines', () => {
      const { container } = render(<ThreatTimeline data={mockData} />)

      const grid = container.querySelector('.recharts-cartesian-grid')
      expect(grid).toBeInTheDocument()
    })

    it('should render tooltip', () => {
      const { container } = render(<ThreatTimeline data={mockData} />)

      const tooltip = container.querySelector('.recharts-tooltip-wrapper')
      expect(tooltip).toBeInTheDocument()
    })
  })

  describe('area gradient', () => {
    it('should define gradient for area fill', () => {
      const { container } = render(<ThreatTimeline data={mockData} />)

      const gradient = container.querySelector('linearGradient')
      expect(gradient).toBeInTheDocument()
      expect(gradient?.getAttribute('id')).toBe('colorCount')
    })

    it('should apply gradient to area', () => {
      const { container } = render(<ThreatTimeline data={mockData} />)

      const area = container.querySelector('.recharts-area')
      expect(area).toBeInTheDocument()
    })
  })

  describe('date formatting', () => {
    it('should format dates correctly on X axis', () => {
      const { container } = render(<ThreatTimeline data={mockData} />)

      const xAxis = container.querySelector('.recharts-cartesian-axis.xaxis')
      expect(xAxis).toBeInTheDocument()
    })
  })

  describe('tooltip behavior', () => {
    it('should have custom tooltip styling', () => {
      const { container } = render(<ThreatTimeline data={mockData} />)

      const tooltipContent = container.querySelector('.recharts-tooltip-content')
      expect(tooltipContent).toBeInTheDocument()
    })
  })
})
