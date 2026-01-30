import { test, expect } from '@playwright/test';

test.describe('Settings & Notifications', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'ultimate@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.goto('/dashboard/settings');
  });

  test('should toggle notification preference and save', async ({ page }) => {
    // Find In-App notification toggle (it's the first one usually)
    const inAppToggle = page.locator('button[role="switch"]').first();
    const initialState = await inAppToggle.getAttribute('class');
    const isInitiallyChecked = initialState?.includes('bg-indigo-600');

    // Click toggle
    await inAppToggle.click();
    
    // Check if Save button appeared
    const saveButton = page.getByRole('button', { name: 'Save' });
    await expect(saveButton).toBeVisible();

    // Click Save
    await saveButton.click();

    // Verify success toast
    await expect(page.getByText('saved')).toBeVisible();
  });
});
