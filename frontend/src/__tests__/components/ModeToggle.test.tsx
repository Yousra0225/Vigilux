import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ModeToggle } from '@/components/mode-toggle'
import { ThemeProvider } from '@/components/theme-provider'

// Mock next-themes since we want to test interaction
const mockSetTheme = vi.fn()
vi.mock('next-themes', () => ({
  useTheme: () => ({
    theme: 'light',
    setTheme: mockSetTheme,
  }),
  ThemeProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}))

describe('ModeToggle', () => {
  it('calls setTheme when clicked', () => {
    render(<ModeToggle />)
    const button = screen.getByRole('button')
    fireEvent.click(button)
    expect(mockSetTheme).toHaveBeenCalledWith('dark')
  })
})
