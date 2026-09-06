import { expect, test } from "@playwright/test";

test.describe("compiled frontend smoke checks", () => {
  test("Hero controls navigate and autoplay advances the active slide", async ({ page }) => {
    await page.goto("/home/");

    const hero = page.locator("[aria-roledescription='carousel']");
    const track = page.locator("#carousel-container");
    const index = hero.locator("[data-carousel-index]");

    await expect(track).toHaveAttribute("data-carousel-initialized", "true");
    await expect(index).toHaveText("01");

    await hero.getByRole("button", { name: /(Next post|Siguiente publicación)/i }).click();
    await expect(index).toHaveText("02");
    await expect(track).toHaveCSS("transform", /matrix\(1, 0, 0, 1, -/);

    await hero.getByRole("button", { name: /(Next post|Siguiente publicación)/i }).click();
    await expect(index).toHaveText("03");
    await hero.getByRole("button", { name: /(Previous post|Publicación anterior)/i }).click();
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

    // Phase 3 requirement: Default is Spanish on cold visit
    await expect(page.locator("html")).toHaveAttribute("lang", "es");

    const languageSelect = page.locator("#language-switcher");
    const languageControl = languageSelect.locator("..");
    await languageControl.getByRole("combobox").click();
    await languageControl.getByRole("option", { name: "en", exact: true }).click();
    await expect(page.locator("html")).toHaveAttribute("lang", "en");

    // Can switch back to Spanish
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
    await expect(menuPanel.locator("#mobile-language-switcher")).toBeVisible();

    await page.goto("/accounts/login/");
    await page.locator("#id_username").fill("e2e-rider@example.test");
    await page.locator("#id_password").fill("e2e-rider-password");
    await page.getByRole("button", { name: /(Sign in|Iniciar sesión)/i }).click();
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

  test("Phase 3: Public Landing and Category Archive render editorial surfaces with The Rider", async ({ page }) => {
    // 1. Public Landing checks
    await page.goto("/");
    await expect(page.locator("h1#landing-hero-title")).toBeVisible();
    await expect(page.locator(".landing-manifesto-card")).toBeVisible();
    await expect(page.locator(".category-card")).toHaveCount(3);
    await expect(page.locator(".landing-community")).toBeVisible();

    // 2. Home keyboard navigation checks
    await page.goto("/home/");
    const hero = page.locator("[aria-roledescription='carousel']");
    const index = hero.locator("[data-carousel-index]");
    await hero.focus();
    await page.keyboard.press("ArrowRight");
    await expect(index).toHaveText("02");
    await page.keyboard.press("ArrowLeft");
    await expect(index).toHaveText("01");

    // 3. Category Archive checks
    await page.goto("/posts/category/builds/");
    await expect(page.locator("h1#category-title")).toBeVisible();
    await expect(page.locator(".category-hero__rider")).toHaveCount(0);
    await expect(page.locator("#sort-select")).toBeVisible();
    await expect(page.locator(".category-post-grid")).toBeVisible();
  });

  test("Phase 4: Article page features reading progress, build specs inspector, author seal, and comment discussion", async ({ page }) => {
    await page.goto("/posts/cafe-racer-de-garaje/");

    // 1. Reading progress bar
    const progressBar = page.locator("#reading-progress");
    await expect(progressBar).toBeAttached();

    // 2. Build specs inspector
    const specsInspector = page.locator(".build-specs-inspector");
    await expect(specsInspector).toBeVisible();
    await expect(specsInspector.locator("h2#specs-heading")).toHaveText(/(Technical Specs Inspector|Inspector de especificaciones técnicas)/);
    await expect(specsInspector.locator(".build-specs-inspector__row").first()).toBeVisible();

    // 3. Author signature seal with The Rider signature badge
    const authorSeal = page.locator(".author-signature-seal");
    await expect(authorSeal).toBeVisible();
    await expect(authorSeal.locator(".author-signature-seal__badge")).toBeVisible();

    // 4. Comments header with The Rider Talking badge
    const commentsHeader = page.locator(".comments-section-header");
    await expect(commentsHeader).toBeVisible();
    await expect(commentsHeader.locator(".comments-section-header__rider")).toBeVisible();
  });

  test("Phase 5: Search interface, clear button, category chips, results highlighting, and zero-results empty card", async ({ page }) => {
    // 1. Search page load with query
    await page.goto("/posts/search/?q=cafe");
    await expect(page.locator(".search-panel")).toBeVisible();
    await expect(page.locator(".search-category-chips")).toBeVisible();

    // 2. Clear button is visible and clears input
    const clearBtn = page.locator("#search-clear-btn");
    await expect(clearBtn).toBeVisible();
    await clearBtn.click();
    await expect(page.locator("#id_q")).toHaveValue("");
    await expect(clearBtn).toBeHidden();

    // 3. Category chips navigation
    const allChip = page.locator(".search-chip").first();
    await expect(allChip).toBeVisible();

    // 4. Zero results empty state
    await page.goto("/posts/search/?q=xyznonexistentterm");
    const emptyCard = page.locator(".search-empty-card");
    await expect(emptyCard).toBeVisible();
    await expect(emptyCard.locator(".search-empty-badge")).toBeVisible();
    await expect(emptyCard.locator(".search-suggestion-pill")).toHaveCount(4);
    await expect(emptyCard.locator(".search-suggestion-pill").first()).toContainText("CB750");
  });

  test("Phase 6: Reader identity, two-step registration, profile hub, and simulated error pages", async ({ page }) => {
    // 1. Two-step registration flow
    await page.goto("/accounts/register/");
    await expect(page.locator(".auth-shell")).toBeVisible();
    await expect(page.locator(".auth-shell__rider")).toBeVisible();

    const timestamp = Date.now();
    const testEmail = `e2e-phase6-${timestamp}@example.test`;
    await page.locator("#id_email").fill(testEmail);
    await page.getByRole("button", { name: /(Continue|Continuar)/i }).click();

    // Step 2 onboarding
    await expect(page).toHaveURL(/\/accounts\/register\/step2\/$/);
    await expect(page.locator(".auth-shell__rider")).toBeVisible();
    await expect(page.locator("[data-avatar-preview-card]")).toBeVisible();
    await page.locator("#id_username").fill(`rider${timestamp}`);
    await page.locator("#id_display_name").fill("Phase 6 Test Rider");
    await page.locator("#id_password1").fill("SecurePass123!");
    await page.locator("#id_password2").fill("SecurePass123!");
    await page.locator("#id_has_motorcycle_0").check();
    await page.getByRole("button", { name: /(Create account|Crear cuenta)/i }).click();

    await expect(page).toHaveURL(/\/home\/$/);

    // Flash messages dismissal check
    const flashMessages = page.locator(".flash-message");
    await expect(flashMessages).toHaveCount(2);
    await flashMessages.first().locator("[data-dismiss-message]").click();
    await expect(flashMessages).toHaveCount(1);
    await flashMessages.first().locator("[data-dismiss-message]").click();
    await expect(flashMessages).toHaveCount(0);

    // 2. Profile hub view
    await page.goto("/accounts/profile/");
    await expect(page.locator(".account-shell")).toBeVisible();
    await expect(page.locator(".profile-avatar-card")).toBeVisible();
    await expect(page.locator(".profile-fleet-card")).toBeVisible();
    await expect(page.locator(".profile-fleet-card")).toContainText(/(Active Garage Rider|Motorista activo de garaje)/);
    await expect(page.locator(".profile-comments-section")).toBeVisible();

    // 3. Simulated error pages
    await page.goto("/404/");
    await expect(page.locator(".error-page")).toBeVisible();
    await expect(page.locator(".error-page .character-badge--xl")).toBeVisible();
    await expect(page.locator(".error-page__action")).toBeVisible();

    await page.goto("/500/");
    await expect(page.locator(".error-page")).toBeVisible();
    await expect(page.locator(".error-page .character-badge--xl")).toBeVisible();
    await expect(page.locator(".error-page__action")).toBeVisible();
  });
});
