// record_demo.js - Automated professional demonstration recording of J.A.R.V.I.S
async (page) => {
  const browser = page.context().browser();
  const videoDir = 'D:\\smart_india_hackathon\\project';
  const finalVideoPath = 'D:\\smart_india_hackathon\\project\\JARVIS_FINAL_DEMO.webm';

  // Create isolated context with video recording at 1440x900 viewport
  const context = await browser.newContext({
    recordVideo: {
      dir: videoDir,
      size: { width: 1440, height: 900 }
    },
    viewport: { width: 1440, height: 900 }
  });

  const recPage = await context.newPage();

  const goBackToDashboard = async () => {
    try {
      const backLink = recPage.locator('a[href="/dashboard"]').first();
      if (await backLink.count() > 0 && await backLink.isVisible()) {
        await backLink.click();
      } else {
        await recPage.goto('http://localhost:5173/dashboard');
      }
      await recPage.waitForURL('**/dashboard', { timeout: 8000 }).catch(() => {});
    } catch (e) {
      await recPage.goto('http://localhost:5173/dashboard');
    }
  };

  try {
    // =========================================================================
    // SCENE 1: PROCUREMENT VERIFICATION DASHBOARD
    // =========================================================================
    console.log('--- SCENE 1: DASHBOARD ---');
    await recPage.goto('http://localhost:5173/dashboard', { waitUntil: 'networkidle' });
    await recPage.waitForTimeout(4000);

    // Smoothly scroll down to showcase Verification Pulse and Recent Verification Activity
    await recPage.evaluate(() => window.scrollBy({ top: 380, behavior: 'smooth' }));
    await recPage.waitForTimeout(3500);

    // =========================================================================
    // SCENE 2: CLEAN PASS VERIFICATION
    // =========================================================================
    console.log('--- SCENE 2: PASS VERIFICATION ---');
    const passLink = recPage.locator('a[href*="PASS_BIDDER"]').first();
    await passLink.scrollIntoViewIfNeeded();
    await recPage.waitForTimeout(1000);
    await passLink.click();

    // Wait for Workbench and dossier to settle
    await recPage.waitForSelector('text=JARVIS_DEMO_PASS_BIDDER', { timeout: 15000 });
    await recPage.getByText('Loading verification dossier...').waitFor({ state: 'hidden', timeout: 15000 }).catch(() => {});
    await recPage.waitForTimeout(4000);

    // Grounding: Bidder Turnover
    console.log('--- PASS: GROUNDING BIDDER TURNOVER ---');
    const turnoverRow = recPage.locator('tr:has-text("REQ-TENDER-0001-004")').first();
    if (await turnoverRow.count() > 0) {
      await turnoverRow.click();
    } else {
      await recPage.locator('tr:has-text("145.00")').first().click();
    }
    await recPage.waitForTimeout(3500);

    // Grounding: OEM Turnover
    console.log('--- PASS: GROUNDING OEM TURNOVER ---');
    const oemRow = recPage.locator('tr:has-text("REQ-TENDER-0001-005")').first();
    if (await oemRow.count() > 0) {
      await oemRow.click();
    } else {
      await recPage.locator('tr:has-text("1,050.00")').first().click();
    }
    await recPage.waitForTimeout(3500);

    // Show Process & Policy tab (MII Class 1 / Policy N/A)
    console.log('--- PASS: PROCESS & POLICY TAB ---');
    const processTab = recPage.locator('button:has-text("Process & Policy")').first();
    if (await processTab.count() > 0) {
      await processTab.click();
      await recPage.waitForTimeout(3000);
      // Return to Obligations tab
      await recPage.locator('button:has-text("Obligations")').first().click();
      await recPage.waitForTimeout(2000);
    }

    // =========================================================================
    // SCENE 3: RETURN TO DASHBOARD
    // =========================================================================
    console.log('--- SCENE 3: RETURN TO DASHBOARD ---');
    await goBackToDashboard();
    await recPage.waitForTimeout(3000);

    // =========================================================================
    // SCENE 4: FAIL VERIFICATION
    // =========================================================================
    console.log('--- SCENE 4: FAIL VERIFICATION ---');
    const failLink = recPage.locator('a[href*="FAIL_BIDDER"]').first();
    await failLink.scrollIntoViewIfNeeded();
    await recPage.waitForTimeout(1000);
    await failLink.click();

    await recPage.waitForSelector('text=JARVIS_DEMO_FAIL_BIDDER', { timeout: 15000 });
    await recPage.getByText('Loading verification dossier...').waitFor({ state: 'hidden', timeout: 15000 }).catch(() => {});
    await recPage.waitForTimeout(4000);

    // Shortfall 1: Turnover (41.67L < 100L)
    console.log('--- FAIL: SHORTFALL 1 - TURNOVER ---');
    const failTurnover = recPage.locator('tr:has-text("REQ-TENDER-0001-004")').first();
    if (await failTurnover.count() > 0) {
      await failTurnover.click();
      await recPage.waitForTimeout(3000);
    }

    // Shortfall 2: OEM Turnover (350L < 800L)
    console.log('--- FAIL: SHORTFALL 2 - OEM TURNOVER ---');
    const failOem = recPage.locator('tr:has-text("REQ-TENDER-0001-005")').first();
    if (await failOem.count() > 0) {
      await failOem.click();
      await recPage.waitForTimeout(3000);
    }

    // Shortfall 3: Experience (1.5Y < 3Y)
    console.log('--- FAIL: SHORTFALL 3 - EXPERIENCE ---');
    const failExp = recPage.locator('tr:has-text("REQ-TENDER-0001-006")').first();
    if (await failExp.count() > 0) {
      await failExp.click();
      await recPage.waitForTimeout(3000);
    }

    // =========================================================================
    // SCENE 5: RETURN TO DASHBOARD
    // =========================================================================
    console.log('--- SCENE 5: RETURN TO DASHBOARD ---');
    await goBackToDashboard();
    await recPage.waitForTimeout(3000);

    // =========================================================================
    // SCENE 6: FORENSIC VERIFICATION
    // =========================================================================
    console.log('--- SCENE 6: FORENSIC VERIFICATION ---');
    const forensicLink = recPage.locator('a[href*="FORENSIC_BIDDER"]').first();
    await forensicLink.scrollIntoViewIfNeeded();
    await recPage.waitForTimeout(1000);
    await forensicLink.click();

    await recPage.waitForSelector('text=JARVIS_DEMO_FORENSIC_BIDDER', { timeout: 15000 });
    await recPage.getByText('Loading verification dossier...').waitFor({ state: 'hidden', timeout: 15000 }).catch(() => {});
    await recPage.waitForTimeout(4000);

    // Open Registries & Contradictions Tab
    console.log('--- FORENSIC: REGISTRIES & CONTRADICTIONS TAB ---');
    const contraTab = recPage.locator('button:has-text("Registries & Contradictions")').first();
    await contraTab.click();
    await recPage.waitForTimeout(3000);

    // Scroll to Contradiction 1 (Turnover)
    console.log('--- FORENSIC: CONTRADICTION 1 (TURNOVER) ---');
    const turnoverContra = recPage.locator('h4:has-text("Turnover contradiction")').first();
    if (await turnoverContra.count() > 0) {
      await turnoverContra.scrollIntoViewIfNeeded();
      await recPage.waitForTimeout(4000);
    } else {
      await recPage.evaluate(() => window.scrollBy({ top: 300, behavior: 'smooth' }));
      await recPage.waitForTimeout(4000);
    }

    // Scroll to Contradiction 2 (Past Performance)
    console.log('--- FORENSIC: CONTRADICTION 2 (PAST PERFORMANCE) ---');
    const pastContra = recPage.locator('h4:has-text("Past performance contradiction")').first();
    if (await pastContra.count() > 0) {
      await pastContra.scrollIntoViewIfNeeded();
      await recPage.waitForTimeout(4000);
    } else {
      await recPage.evaluate(() => window.scrollBy({ top: 350, behavior: 'smooth' }));
      await recPage.waitForTimeout(4000);
    }

    // =========================================================================
    // SCENE 7: REVIEW QUEUE
    // =========================================================================
    console.log('--- SCENE 7: REVIEW QUEUE ---');
    const routeBtn = recPage.locator('button:has-text("Route to Review")').first();
    if (await routeBtn.count() > 0 && await routeBtn.isVisible()) {
      await routeBtn.click();
    } else {
      await recPage.goto('http://localhost:5173/review', { waitUntil: 'networkidle' });
    }
    await recPage.waitForTimeout(4500);

    // =========================================================================
    // SCENE 8: RETURN TO DASHBOARD & CLOSING SHOT
    // =========================================================================
    console.log('--- SCENE 8: DASHBOARD CLOSING SHOT ---');
    await recPage.goto('http://localhost:5173/dashboard', { waitUntil: 'networkidle' });
    await recPage.waitForTimeout(2000);
    // Smooth scroll down to display all recent verified records in history
    await recPage.evaluate(() => window.scrollBy({ top: 400, behavior: 'smooth' }));
    // Hold final shot for 6 seconds
    await recPage.waitForTimeout(6000);

    console.log('--- DEMO SEQUENCE COMPLETED SUCCESSFULLY ---');
  } finally {
    const video = recPage.video();
    await recPage.close();
    await context.close();

    if (video) {
      await video.saveAs(finalVideoPath);
      console.log('Saved final video to:', finalVideoPath);
    }
  }

  return {
    finalVideoPath,
    status: 'RECORDING_COMPLETE'
  };
}
