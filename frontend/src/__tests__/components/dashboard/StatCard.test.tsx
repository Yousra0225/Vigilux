import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { StatCard } from '@/components/dashboard/StatCard'
import { Activity } from 'lucide-react'

describe('StatCard', () => {
  it('renders title and value', () => {
    render(<StatCard title="Total Users" value="1,234" icon={Activity} />)
    expect(screen.getByText('Total Users')).toBeInTheDocument()
    expect(screen.getByText('1,234')).toBeInTheDocument()
  })

  it('renders description when provided', () => {
    render(<StatCard title="Growth" value="15%" icon={Activity} description="Since last month" />)
    expect(screen.getByText('Since last month')).toBeInTheDocument()
  })
})