import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('should allow a user to log in', async ({ page }) => {
    await page.goto('/login');

    await page.fill('input[type="email"]', 'starter@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Wait for navigation to dashboard
    await expect(page).toHaveURL(/\/dashboard/);
    
    // Verify dashboard content matches "My Workspace" or similar
    await expect(page.getByText('My Workspace')).toBeVisible();
  });
});
