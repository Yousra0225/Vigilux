import { test, expect } from '@playwright/test';

test.describe('Dashboard Visibility', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'starter@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');
  });

  test('should display stats cards', async ({ page }) => {
    await expect(page.getByText('Total Competitors')).toBeVisible();
    await expect(page.getByText('Breakthrough Signals')).toBeVisible();
    await expect(page.getByText('Avg Threat Score')).toBeVisible();
  });

  test('should display threat timeline', async ({ page }) => {
    // Check for the chart container
    await expect(page.locator('.recharts-responsive-container')).toBeVisible();
  });
});
