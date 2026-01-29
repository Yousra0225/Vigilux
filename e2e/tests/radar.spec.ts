import { test, expect } from '@playwright/test';

test.describe('Radar Feature', () => {
  
  test('Starter plan should see blurred results and upgrade prompt', async ({ page }) => {
    // Login as Starter
    await page.goto('/login');
    await page.fill('input[type="email"]', 'starter@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/\/dashboard/);

    // Go to Radar
    await page.goto('/dashboard/radar');

    // Search
    await page.fill('input[placeholder*="Search"]', 'tech');
    await page.click('button:has-text("Scan Market")');

    // Wait for results
    // We expect results to appear. The mocked API returns results.
    // Check for the "Growth Plan Required" overlay
    await expect(page.getByText('Growth Plan Required')).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole('button', { name: 'Upgrade Now' })).toBeVisible();
  });

  test('Ultimate plan should see full results', async ({ page }) => {
    // Login as Ultimate
    await page.goto('/login');
    await page.fill('input[type="email"]', 'ultimate@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/\/dashboard/);

    // Go to Radar
    await page.goto('/dashboard/radar');

    // Search
    await page.fill('input[placeholder*="Search"]', 'tech');
    await page.click('button:has-text("Scan Market")');

    // Wait for results
    // We expect results to appear.
    // Check that "Growth Plan Required" is NOT visible
    await expect(page.getByText('Growth Plan Required')).not.toBeVisible({ timeout: 10000 });
    
    // Check for insights content
    await expect(page.getByText('AI Insights').first()).toBeVisible();
  });
});
