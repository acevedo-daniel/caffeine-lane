import { expect, test } from "@playwright/test";

test.describe("compiled frontend smoke checks", () => {
  test("Hero controls navigate and autoplay advances the active slide", async ({ page }) => {
    await page.goto("/home/");

    const hero = page.locator("[aria-roledescription='carousel']");
    const track = page.locator("#carousel-container");
    const index = hero.locator("[data-carousel-index]");

    await expect(track).toHaveAttribute("data-carousel-initialized", "true");
    await expect(index).toHaveText("01");

    await hero.getByRole("button", { name: "Next post" }).click();
    await expect(index).toHaveText("02");
    await expect(track).toHaveCSS("transform", /matrix\(1, 0, 0, 1, -/);

    await hero.getByRole("button", { name: "Next post" }).click();
    await expect(index).toHaveText("03");
    await hero.getByRole("button", { name: "Previous post" }).click();
    await expect(index).toHaveText("02");

    await page.mouse.move(0, 0);
    await expect(index).not.toHaveText("02", { timeout: 9_000 });
  });

  test("Hero disables autoplay when reduced motion is requested", async ({ page }) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.goto("/home/");

    const index = page.locator("[aria-roledescription='carousel'] [data-carousel-index]");
    await expect(index).toHaveText("01");
    await page.waitForTimeout(7_500);
    await expect(index).toHaveText("01");
  });

  test("language and custom selects synchronize with their native controls", async ({ page }) => {
    await page.goto("/home/");

    const languageSelect = page.locator("#language-switcher");
    const languageControl = languageSelect.locator("..");
    await languageControl.getByRole("combobox").click();
    await languageControl.getByRole("option", { name: "es", exact: true }).click();
    await expect(page.locator("html")).toHaveAttribute("lang", "es");

    await page.goto("/posts/search/");
    const categorySelect = page.locator("#id_category");
    const categoryControl = categorySelect.locator("..");
    const initialCategoryValue = await categorySelect.inputValue();
    await categoryControl.getByRole("combobox").click();
    await categoryControl.getByRole("option").nth(1).click();
    await expect(categorySelect).not.toHaveValue(initialCategoryValue);
  });

  test("the mobile navigation opens and the reply composer remains progressive", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 800 });
    await page.goto("/home/");

    const menuButton = page.locator("[data-mobile-menu-button]");
    const menuPanel = page.locator("[data-mobile-menu-panel]");
    await expect(menuButton).toHaveAttribute("aria-expanded", "false");
    await menuButton.click();
    await expect(menuButton).toHaveAttribute("aria-expanded", "true");
    await expect(menuPanel).toHaveClass(/is-open/);

    await page.goto("/accounts/login/");
    await page.locator("#id_username").fill("e2e-rider@example.test");
    await page.locator("#id_password").fill("e2e-rider-password");
    await page.getByRole("button", { name: "Sign in" }).click();
    await expect(page).toHaveURL(/\/home\/$/);

    await page.goto("/posts/cafe-racer-de-garaje/");
    const replyToggle = page.locator("[data-reply-open]").first();
    const replyForm = page.locator("[data-reply-form]").first();
    await expect(replyForm).toBeHidden();
    await replyToggle.click();
    await expect(replyToggle).toHaveAttribute("aria-expanded", "true");
    await expect(replyForm).toBeVisible();
    await expect(replyForm.locator("textarea")).toBeFocused();
    await replyForm.locator("[data-reply-cancel]").click();
    await expect(replyForm).toBeHidden();
  });
});
