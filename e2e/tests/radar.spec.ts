import { test, expect } from '@playwright/test';

test.describe('Radar Logic & Plan Restrictions', () => {
  
  test('Starter plan should see blurred insights', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'starter@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    await page.goto('/dashboard/radar');
    await page.click('button:has-text("Scan Market")');

    // Wait for results
    await expect(page.getByText('Growth Plan Required')).toBeVisible();
    // Check for blur class or overlay
    await expect(page.locator('.blur-\[3px\]')).toBeVisible();
  });

  test('Ultimate plan should see full insights', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'ultimate@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    await page.goto('/dashboard/radar');
    await page.click('button:has-text("Scan Market")');

    // Wait for results
    await expect(page.getByText('Growth Plan Required')).not.toBeVisible();
    await expect(page.getByText('AI Insights').first()).toBeVisible();
  });
});

