import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '../../utils/test-utils'
import { QuickViewModal, CompetitorDetail } from '@/components/competitors/QuickViewModal'

const mockCompetitor: CompetitorDetail = {
  id: '1',
  name: 'TechCorp Inc',
  url: 'https://techcorp.com',
  score: 85,
  pitch: 'Leading provider of AI-powered business intelligence solutions for enterprise clients.',
  estimated_revenue: '$50M - $100M',
  strengths: [
    'Strong AI technology stack',
    'Enterprise-grade security',
    'Excellent customer support',
  ],
  weaknesses: [
    'Higher pricing than competitors',
    'Limited mobile app functionality',
  ],
  market_sentiment: 'Positive',
  tracking_status: 'active',
}

describe('QuickViewModal', () => {
  describe('when closed', () => {
    it('should not render anything when isOpen is false', () => {
      const { container } = render(
        <QuickViewModal
          competitor={mockCompetitor}
          isOpen={false}
          onClose={vi.fn()}
          loading={false}
        />
      )

      expect(container.firstChild).toBeNull()
    })
  })

  describe('when open', () => {
    it('should render the modal when isOpen is true', () => {
      render(
        <QuickViewModal
          competitor={mockCompetitor}
          isOpen={true}
          onClose={vi.fn()}
          loading={false}
        />
      )

      expect(screen.getByText('TechCorp Inc')).toBeInTheDocument()
    })

    it('should render modal with overlay', () => {
      const { container } = render(
        <QuickViewModal
          competitor={mockCompetitor}
          isOpen={true}
          onClose={vi.fn()}
          loading={false}
        />
      )

      const overlay = container.querySelector('.bg-black\\/50')
      expect(overlay).toBeInTheDocument()
    })

    it('should render modal content', () => {
      const { container } = render(
        <QuickViewModal
          competitor={mockCompetitor}
          isOpen={true}
          onClose={vi.fn()}
          loading={false}
        />
      )

      const modal = container.querySelector('.bg-white.dark\\:bg-gray-900')
      expect(modal).toBeInTheDocument()
    })
  })

  describe('loading state', () => {
    it('should show loading state when competitor is null', () => {
      render(
        <QuickViewModal
          competitor={null}
          isOpen={true}
          onClose={vi.fn()}
          loading={true}
        />
      )

      expect(screen.getByText('Loading...')).toBeInTheDocument()
    })

    it('should render skeleton loaders', () => {
      const { container } = render(
        <QuickViewModal
          competitor={null}
          isOpen={true}
          onClose={vi.fn()}
          loading={true}
        />
      )

      const skeletons = container.querySelectorAll('.animate-pulse')
      expect(skeletons.length).toBeGreaterThan(0)
    })
  })

  describe('header', () => {
    it('should render competitor name', () => {
      render(
        <QuickViewModal
          competitor={mockCompetitor}
          isOpen={true}
          onClose={vi.fn()}
          loading={false}
        />
      )

      expect(screen.getByText('TechCorp Inc')).toBeInTheDocument()
    })

    it('should render competitor URL when present', () => {
      render(
        <QuickViewModal
          competitor={mockCompetitor}
          isOpen={true}
          onClose={vi.fn()}
          loading={false}
        />
      )

      expect(screen.getByText('techcorp.com')).toBeInTheDocument()
    })

    it('should not render URL when not present', () => {
      const competitorWithoutUrl = { ...mockCompetitor, url: undefined }

      render(
        <QuickViewModal
          competitor={competitorWithoutUrl}
          isOpen={true}
          onClose={vi.fn()}
          loading={false}
        />
      )

      expect(screen.queryByText('techcorp.com')).not.toBeInTheDocument()
    })

    it('should render close button', () => {
      render(
        <QuickViewModal
          competitor={mockCompetitor}
          isOpen={true}
          onClose={vi.fn()}
          loading={false}
        />
      )

      const closeButton = screen.getByRole('button').querySelector('.lucide-x')
      expect(closeButton).toBeInTheDocument()
    })

    it('should show first letter of company name in avatar', () => {
      render(
        <QuickViewModal
          competitor={mockCompetitor}
          isOpen={true}
          onClose={vi.fn()}
          loading={false}
        />
      )

      expect(screen.getByText('T')).toBeInTheDocument()
    })
  })

  describe('content sections', () => {
    it('should render AI pitch section', () => {
      render(
        <QuickViewModal
          competitor={mockCompetitor}
          isOpen={true}
          onClose={vi.fn()}
          loading={false}
        />
      )

      expect(screen.getByText('AI Pitch')).toBeInTheDocument()
      expect(screen.getByText(/leading provider of ai-powered/i)).toBeInTheDocument()
    })

    it('should render stats grid', () => {
      render(
        <QuickViewModal
          competitor={mockCompetitor}
          isOpen={true}
          onClose={vi.fn()}
          loading={false}
        />
      )

      expect(screen.getByText('Threat Score')).toBeInTheDocument()
      expect(screen.getByText('Est. Revenue')).toBeInTheDocument()
      expect(screen.getByText('Sentiment')).toBeInTheDocument()
    })

    it('should render stats values', () => {
      render(
        <QuickViewModal
          competitor={mockCompetitor}
          isOpen={true}
          onClose={vi.fn()}
          loading={false}
        />
      )

      expect(screen.getByText('85/100')).toBeInTheDocument()
      expect(screen.getByText('$50M - $100M')).toBeInTheDocument()
      expect(screen.getByText('Positive')).toBeInTheDocument()
    })

    it('should render strengths section', () => {
      render(
        <QuickViewModal
          competitor={mockCompetitor}
          isOpen={true}
          onClose={vi.fn()}
          loading={false}
        />
      )

      expect(screen.getByText('Strengths')).toBeInTheDocument()
      expect(screen.getByText('Strong AI technology stack')).toBeInTheDocument()
      expect(screen.getByText('Enterprise-grade security')).toBeInTheDocument()
      expect(screen.getByText('Excellent customer support')).toBeInTheDocument()
    })

    it('should render weaknesses section', () => {
      render(
        <QuickViewModal
          competitor={mockCompetitor}
          isOpen={true}
          onClose={vi.fn()}
          loading={false}
        />
      )

      expect(screen.getByText('Weaknesses')).toBeInTheDocument()
      expect(screen.getByText('Higher pricing than competitors')).toBeInTheDocument()
      expect(screen.getByText('Limited mobile app functionality')).toBeInTheDocument()
    })
  })

  describe('interactions', () => {
    it('should call onClose when close button is clicked', () => {
      const onClose = vi.fn()

      render(
        <QuickViewModal
          competitor={mockCompetitor}
          isOpen={true}
          onClose={onClose}
          loading={false}
        />
      )

      const closeButton = screen.getByRole('button').querySelector('.lucide-x')?.closest('button')
      fireEvent.click(closeButton!)

      expect(onClose).toHaveBeenCalledOnce()
    })

    it('should call onClose when footer close button is clicked', () => {
      const onClose = vi.fn()

      render(
        <QuickViewModal
          competitor={mockCompetitor}
          isOpen={true}
          onClose={onClose}
          loading={false}
        />
      )

      const footerButton = screen.getByText('Close')
      fireEvent.click(footerButton)

      expect(onClose).toHaveBeenCalledOnce()
    })

    it('should call onClose when overlay is clicked', () => {
      const onClose = vi.fn()
      const { container } = render(
        <QuickViewModal
          competitor={mockCompetitor}
          isOpen={true}
          onClose={onClose}
          loading={false}
        />
      )

      const overlay = container.querySelector('.bg-black\\/50')
      fireEvent.click(overlay!)

      expect(onClose).toHaveBeenCalledOnce()
    })

    it('should not call onClose when modal content is clicked', () => {
      const onClose = vi.fn()
      const { container } = render(
        <QuickViewModal
          competitor={mockCompetitor}
          isOpen={true}
          onClose={onClose}
          loading={false}
        />
      )

      const modalContent = container.querySelector('.bg-white.dark\\:bg-gray-900.max-w-2xl')
      fireEvent.click(modalContent!)

      expect(onClose).not.toHaveBeenCalled()
    })
  })

  describe('external links', () => {
    it('should render link with correct attributes', () => {
      render(
        <QuickViewModal
          competitor={mockCompetitor}
          isOpen={true}
          onClose={vi.fn()}
          loading={false}
        />
      )

      const link = screen.getByText('techcorp.com').closest('a')
      expect(link).toHaveAttribute('href', 'https://techcorp.com')
      expect(link).toHaveAttribute('target', '_blank')
      expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    })
  })

  describe('responsive design', () => {
    it('should apply responsive classes', () => {
      const { container } = render(
        <QuickViewModal
          competitor={mockCompetitor}
          isOpen={true}
          onClose={vi.fn()}
          loading={false}
        />
      )

      const statsGrid = container.querySelector('.grid-cols-1.sm\\:grid-cols-3')
      expect(statsGrid).toBeInTheDocument()

      const strengthsWeaknessesGrid = container.querySelector('.grid-cols-1.md\\:grid-cols-2')
      expect(strengthsWeaknessesGrid).toBeInTheDocument()
    })
  })
})
