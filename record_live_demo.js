// record_live_demo.js - Continuous professional demonstration of J.A.R.V.I.S running the verification pipeline 3 separate times live
async (page) => {
  const browser = page.context().browser();
  const videoDir = 'D:\\smart_india_hackathon\\project';
  const finalVideoPath = 'D:\\smart_india_hackathon\\project\\JARVIS_FINAL_LIVE_PIPELINE_DEMO.webm';

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

  const recordedRuns = {};

  try {
    // =========================================================================
    // INTRO: PROCUREMENT VERIFICATION DASHBOARD
    // =========================================================================
    console.log('--- INTRO: PROCUREMENT DASHBOARD ---');
    await recPage.goto('http://localhost:5173/dashboard', { waitUntil: 'networkidle' });
    await recPage.waitForTimeout(3500);

    // =========================================================================
    // CYCLE 1: PASS BIDDER LIVE PIPELINE EXECUTION
    // =========================================================================
    console.log('--- CYCLE 1: PASS BIDDER RUN ---');
    await recPage.locator('a[href="/verify/new"]').first().click();
    await recPage.waitForURL('**/verify/new', { timeout: 8000 });
    await recPage.waitForTimeout(2000);

    // Upload Tender and PASS Bidder PDFs
    console.log('Uploading tender and PASS bidder PDFs...');
    const tenderInput1 = recPage.locator('label:has-text("Browse PDF") input[type="file"]');
    await tenderInput1.setInputFiles('D:\\smart_india_hackathon\\project\\video_pdf.pdf');
    await recPage.waitForTimeout(1500);

    const bidInput1 = recPage.locator('label:has-text("Browse files") input[type="file"]');
    await bidInput1.setInputFiles('D:\\smart_india_hackathon\\project\\JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf');
    await recPage.waitForTimeout(2000);

    // Trigger verification pipeline
    console.log('Triggering pipeline for PASS case...');
    const runBtn1 = recPage.locator('button:has-text("Run verification pipeline")');
    await runBtn1.scrollIntoViewIfNeeded();
    await recPage.waitForTimeout(1000);
    await runBtn1.click();

    // Observe 6-stage live execution progression
    await recPage.waitForSelector('text=Verification Complete', { timeout: 45000 });
    const passVerifId = await recPage.locator('span:has-text("ID: VERIF-")').textContent();
    recordedRuns['PASS'] = passVerifId.trim();
    console.log('PASS pipeline completed live! Result:', recordedRuns['PASS']);

    // Showcase completed PASS summary card
    await recPage.waitForTimeout(3500);

    // Open newly generated Workbench
    console.log('Opening PASS Workbench...');
    await recPage.locator('button:has-text("Open Verification Workbench")').click();
    await recPage.waitForSelector('text=JARVIS_DEMO_PASS_BIDDER', { timeout: 15000 });
    await recPage.getByText('Loading verification dossier...').waitFor({ state: 'hidden', timeout: 15000 }).catch(() => {});
    await recPage.waitForTimeout(3500);

    // Inspect Bidder Turnover Grounding
    const pTurnover = recPage.locator('tr:has-text("REQ-TENDER-0001-004")').first();
    if (await pTurnover.count() > 0) {
      await pTurnover.click();
    } else {
      await recPage.locator('tr:has-text("145.00")').first().click();
    }
    await recPage.waitForTimeout(3500);

    // Inspect OEM Turnover Grounding
    const pOem = recPage.locator('tr:has-text("REQ-TENDER-0001-005")').first();
    if (await pOem.count() > 0) {
      await pOem.click();
    } else {
      await recPage.locator('tr:has-text("1,050.00")').first().click();
    }
    await recPage.waitForTimeout(3000);

    // Return to Dashboard and observe new run in Recent Activity
    await goBackToDashboard();
    await recPage.evaluate(() => window.scrollBy({ top: 350, behavior: 'smooth' }));
    await recPage.waitForTimeout(3000);

    // =========================================================================
    // CYCLE 2: FAIL BIDDER LIVE PIPELINE EXECUTION
    // =========================================================================
    console.log('--- CYCLE 2: FAIL BIDDER RUN ---');
    await recPage.locator('a[href="/verify/new"]').first().click();
    await recPage.waitForURL('**/verify/new', { timeout: 8000 });
    await recPage.waitForTimeout(2000);

    // Upload Tender and FAIL Bidder PDFs
    console.log('Uploading tender and FAIL bidder PDFs...');
    const tenderInput2 = recPage.locator('label:has-text("Browse PDF") input[type="file"]');
    await tenderInput2.setInputFiles('D:\\smart_india_hackathon\\project\\video_pdf.pdf');
    await recPage.waitForTimeout(1500);

    const bidInput2 = recPage.locator('label:has-text("Browse files") input[type="file"]');
    await bidInput2.setInputFiles('D:\\smart_india_hackathon\\project\\JARVIS_DEMO_FAIL_BIDDER_GEM_2026_B_7959150.pdf');
    await recPage.waitForTimeout(2000);

    // Trigger verification pipeline
    console.log('Triggering pipeline for FAIL case...');
    const runBtn2 = recPage.locator('button:has-text("Run verification pipeline")');
    await runBtn2.scrollIntoViewIfNeeded();
    await recPage.waitForTimeout(1000);
    await runBtn2.click();

    // Observe 6-stage live execution progression
    await recPage.waitForSelector('text=Verification Complete', { timeout: 45000 });
    const failVerifId = await recPage.locator('span:has-text("ID: VERIF-")').textContent();
    recordedRuns['FAIL'] = failVerifId.trim();
    console.log('FAIL pipeline completed live! Result:', recordedRuns['FAIL']);

    // Showcase completed FAIL summary card
    await recPage.waitForTimeout(3500);

    // Open newly generated Workbench
    console.log('Opening FAIL Workbench...');
    await recPage.locator('button:has-text("Open Verification Workbench")').click();
    await recPage.waitForSelector('text=JARVIS_DEMO_FAIL_BIDDER', { timeout: 15000 });
    await recPage.getByText('Loading verification dossier...').waitFor({ state: 'hidden', timeout: 15000 }).catch(() => {});
    await recPage.waitForTimeout(3500);

    // Inspect Turnover shortfall
    const fTurnover = recPage.locator('tr:has-text("REQ-TENDER-0001-004")').first();
    if (await fTurnover.count() > 0) {
      await fTurnover.click();
      await recPage.waitForTimeout(3000);
    }

    // Inspect OEM Turnover shortfall
    const fOem = recPage.locator('tr:has-text("REQ-TENDER-0001-005")').first();
    if (await fOem.count() > 0) {
      await fOem.click();
      await recPage.waitForTimeout(3000);
    }

    // Inspect Experience shortfall
    const fExp = recPage.locator('tr:has-text("REQ-TENDER-0001-006")').first();
    if (await fExp.count() > 0) {
      await fExp.click();
      await recPage.waitForTimeout(3000);
    }

    // Return to Dashboard and observe new run in Recent Activity
    await goBackToDashboard();
    await recPage.evaluate(() => window.scrollBy({ top: 350, behavior: 'smooth' }));
    await recPage.waitForTimeout(3000);

    // =========================================================================
    // CYCLE 3: FORENSIC BIDDER LIVE PIPELINE EXECUTION
    // =========================================================================
    console.log('--- CYCLE 3: FORENSIC BIDDER RUN ---');
    await recPage.locator('a[href="/verify/new"]').first().click();
    await recPage.waitForURL('**/verify/new', { timeout: 8000 });
    await recPage.waitForTimeout(2000);

    // Upload Tender and FORENSIC Bidder PDFs
    console.log('Uploading tender and FORENSIC bidder PDFs...');
    const tenderInput3 = recPage.locator('label:has-text("Browse PDF") input[type="file"]');
    await tenderInput3.setInputFiles('D:\\smart_india_hackathon\\project\\video_pdf.pdf');
    await recPage.waitForTimeout(1500);

    const bidInput3 = recPage.locator('label:has-text("Browse files") input[type="file"]');
    await bidInput3.setInputFiles('D:\\smart_india_hackathon\\project\\JARVIS_DEMO_FORENSIC_BIDDER_GEM_2026_B_7959150.pdf');
    await recPage.waitForTimeout(2000);

    // Trigger verification pipeline
    console.log('Triggering pipeline for FORENSIC case...');
    const runBtn3 = recPage.locator('button:has-text("Run verification pipeline")');
    await runBtn3.scrollIntoViewIfNeeded();
    await recPage.waitForTimeout(1000);
    await runBtn3.click();

    // Observe 6-stage live execution progression
    await recPage.waitForSelector('text=Verification Complete', { timeout: 45000 });
    const forVerifId = await recPage.locator('span:has-text("ID: VERIF-")').textContent();
    recordedRuns['FORENSIC'] = forVerifId.trim();
    console.log('FORENSIC pipeline completed live! Result:', recordedRuns['FORENSIC']);

    // Showcase completed FORENSIC summary card
    await recPage.waitForTimeout(3500);

    // Open newly generated Workbench
    console.log('Opening FORENSIC Workbench...');
    await recPage.locator('button:has-text("Open Verification Workbench")').click();
    await recPage.waitForSelector('text=JARVIS_DEMO_FORENSIC_BIDDER', { timeout: 15000 });
    await recPage.getByText('Loading verification dossier...').waitFor({ state: 'hidden', timeout: 15000 }).catch(() => {});
    await recPage.waitForTimeout(3500);

    // Open Registries & Contradictions Tab
    const contraTab = recPage.locator('button:has-text("Registries & Contradictions")').first();
    await contraTab.click();
    await recPage.waitForTimeout(2500);

    // Contradiction 1: Turnover
    const turnoverContra = recPage.locator('h4:has-text("Turnover contradiction")').first();
    if (await turnoverContra.count() > 0) {
      await turnoverContra.scrollIntoViewIfNeeded();
      await recPage.waitForTimeout(4000);
    } else {
      await recPage.evaluate(() => window.scrollBy({ top: 300, behavior: 'smooth' }));
      await recPage.waitForTimeout(4000);
    }

    // Contradiction 2: Past Performance
    const pastContra = recPage.locator('h4:has-text("Past performance contradiction")').first();
    if (await pastContra.count() > 0) {
      await pastContra.scrollIntoViewIfNeeded();
      await recPage.waitForTimeout(4000);
    } else {
      await recPage.evaluate(() => window.scrollBy({ top: 350, behavior: 'smooth' }));
      await recPage.waitForTimeout(4000);
    }

    // Open Review Queue
    console.log('Opening Review Queue...');
    const routeBtn = recPage.locator('button:has-text("Route to Review")').first();
    if (await routeBtn.count() > 0 && await routeBtn.isVisible()) {
      await routeBtn.click();
    } else {
      await recPage.goto('http://localhost:5173/review', { waitUntil: 'networkidle' });
    }
    await recPage.waitForTimeout(4000);

    // =========================================================================
    // FINAL DASHBOARD CLOSING SHOT
    // =========================================================================
    console.log('--- CLOSING SHOT: DASHBOARD RECENT ACTIVITY ---');
    await recPage.goto('http://localhost:5173/dashboard', { waitUntil: 'networkidle' });
    await recPage.waitForTimeout(2500);
    await recPage.evaluate(() => window.scrollBy({ top: 380, behavior: 'smooth' }));
    await recPage.waitForTimeout(6000);

    console.log('--- ALL 3 LIVE RUNS RECORDED SUCCESSFULLY ---');
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
    recordedRuns,
    status: 'LIVE_RECORDING_COMPLETE'
  };
}
