// record_final_live_demo.js - Continuous professional demonstration of J.A.R.V.I.S:
// PART 1: Three Live Pipeline Verifications (PASS, FAIL, FORENSIC) with fresh execution and Workbench inspection
// PART 2: Consolidated Complete Website Tour (Dashboard, Intake, Workbench, Matrix, Explainability, Process/Policy, Contradictions, Review Queue, Audit Dossier, Closing Shot)
// All with a clearly visible, smooth cursor/pointer.

async (page) => {
  const browser = page.context().browser();
  const videoDir = 'D:\\smart_india_hackathon\\project';
  const finalVideoPath = 'D:\\smart_india_hackathon\\project\\JARVIS_FINAL_LIVE_DEMO.webm';

  // Create isolated context with video recording at 1440x900 viewport
  const context = await browser.newContext({
    recordVideo: {
      dir: videoDir,
      size: { width: 1440, height: 900 }
    },
    viewport: { width: 1440, height: 900 }
  });

  // Inject high-visibility custom pointer cursor and click effect across all pages
  await context.addInitScript(() => {
    window.addEventListener('DOMContentLoaded', () => {
      if (document.getElementById('playwright-custom-cursor')) return;

      const cursorContainer = document.createElement('div');
      cursorContainer.id = 'playwright-custom-cursor';
      cursorContainer.style.position = 'fixed';
      cursorContainer.style.top = '0';
      cursorContainer.style.left = '0';
      cursorContainer.style.width = '0';
      cursorContainer.style.height = '0';
      cursorContainer.style.zIndex = '999999999';
      cursorContainer.style.pointerEvents = 'none';

      // SVG mouse pointer icon with high visibility drop shadow
      const cursor = document.createElement('div');
      cursor.id = 'cursor-pointer-icon';
      cursor.style.position = 'absolute';
      cursor.style.width = '26px';
      cursor.style.height = '26px';
      cursor.style.transform = 'translate(-2px, -2px)';
      cursor.style.transition = 'transform 0.08s ease-out';
      cursor.innerHTML = `
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter: drop-shadow(0 2px 5px rgba(0,0,0,0.55));">
          <path d="M4 3L11.5 21L14.5 13.5L22 10.5L4 3Z" fill="#2563EB" stroke="#FFFFFF" stroke-width="2.2" stroke-linejoin="round"/>
        </svg>
      `;

      // Click ripple pulse
      const clickRipple = document.createElement('div');
      clickRipple.id = 'cursor-click-ripple';
      clickRipple.style.position = 'absolute';
      clickRipple.style.width = '36px';
      clickRipple.style.height = '36px';
      clickRipple.style.borderRadius = '50%';
      clickRipple.style.border = '2.5px solid #2563EB';
      clickRipple.style.backgroundColor = 'rgba(37, 99, 235, 0.25)';
      clickRipple.style.transform = 'translate(-18px, -18px) scale(0)';
      clickRipple.style.transition = 'transform 0.25s ease-out, opacity 0.25s ease-out';
      clickRipple.style.opacity = '0';
      clickRipple.style.pointerEvents = 'none';

      cursorContainer.appendChild(clickRipple);
      cursorContainer.appendChild(cursor);
      document.body.appendChild(cursorContainer);

      const updatePosition = (x, y) => {
        cursor.style.left = `${x}px`;
        cursor.style.top = `${y}px`;
        clickRipple.style.left = `${x}px`;
        clickRipple.style.top = `${y}px`;
      };

      document.addEventListener('mousemove', (e) => {
        updatePosition(e.clientX, e.clientY);
      }, { passive: true });

      document.addEventListener('mousedown', (e) => {
        updatePosition(e.clientX, e.clientY);
        cursor.style.transform = 'translate(-2px, -2px) scale(0.85)';
        clickRipple.style.transform = 'translate(-18px, -18px) scale(1)';
        clickRipple.style.opacity = '1';
      }, { passive: true });

      document.addEventListener('mouseup', (e) => {
        cursor.style.transform = 'translate(-2px, -2px) scale(1)';
        clickRipple.style.transform = 'translate(-18px, -18px) scale(1.6)';
        clickRipple.style.opacity = '0';
      }, { passive: true });
    });
  });

  const recPage = await context.newPage();

  // Helper functions for visible cursor movement and clicks
  const movePointerTo = async (locator) => {
    try {
      const box = await locator.boundingBox();
      if (box) {
        const targetX = box.x + box.width / 2;
        const targetY = box.y + box.height / 2;
        await recPage.mouse.move(targetX, targetY, { steps: 10 });
        await recPage.waitForTimeout(180);
      }
    } catch (e) {}
  };

  const moveAndClick = async (locator, options = {}) => {
    try {
      await locator.scrollIntoViewIfNeeded();
      await recPage.waitForTimeout(150);
      const box = await locator.boundingBox();
      if (box) {
        const targetX = box.x + box.width / 2;
        const targetY = box.y + box.height / 2;
        await recPage.mouse.move(targetX, targetY, { steps: 10 });
        await recPage.waitForTimeout(180);
      }
      await locator.click(options);
      await recPage.waitForTimeout(300);
    } catch (e) {
      await locator.click(options).catch(() => {});
    }
  };

  const goBackToDashboard = async () => {
    try {
      const backLink = recPage.locator('a[href="/dashboard"]').first();
      if (await backLink.count() > 0 && await backLink.isVisible()) {
        await moveAndClick(backLink);
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
    // Initial mouse position
    await recPage.mouse.move(720, 450, { steps: 5 });

    // =========================================================================
    // PART 1 — CYCLE 1: PASS BIDDER LIVE PIPELINE EXECUTION
    // =========================================================================
    console.log('>>> [PART 1 - CYCLE 1] PASS BIDDER RUN');
    await recPage.goto('http://localhost:5173/dashboard', { waitUntil: 'networkidle' });
    await recPage.waitForTimeout(2000);

    // Navigate to New Bid Verification
    const newVerifLink1 = recPage.locator('a[href="/verify/new"]').first();
    await moveAndClick(newVerifLink1);
    await recPage.waitForURL('**/verify/new', { timeout: 8000 });
    await recPage.waitForTimeout(1500);

    // 1. Upload Tender PDF
    console.log('Uploading Tender PDF...');
    const tenderInput1 = recPage.locator('label:has-text("Browse PDF") input[type="file"]');
    await tenderInput1.setInputFiles('D:\\smart_india_hackathon\\project\\video_pdf.pdf');
    await recPage.waitForSelector('text=PDF accepted', { timeout: 10000 });
    await recPage.waitForTimeout(800);

    // 2. Upload PASS Bidder PDF
    console.log('Uploading PASS Bidder PDF...');
    const bidInput1 = recPage.locator('label:has-text("Browse files") input[type="file"]');
    await bidInput1.setInputFiles('D:\\smart_india_hackathon\\project\\JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf');
    await recPage.waitForSelector('span:has-text("1 file")', { timeout: 10000 });
    await recPage.waitForSelector('text=JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf', { timeout: 10000 });
    await recPage.waitForTimeout(1200);

    // 3. Move cursor to Run Verification Pipeline button and trigger
    console.log('Triggering PASS live verification pipeline...');
    const runBtn1 = recPage.locator('button:has-text("Run verification pipeline")');
    await moveAndClick(runBtn1);

    // 4. Visibly observe 6-stage live execution progression
    await recPage.waitForSelector('text=Verification Complete', { timeout: 45000 });
    const passVerifId = await recPage.locator('span:has-text("ID: VERIF-")').textContent();
    recordedRuns['PASS'] = passVerifId.trim();
    console.log('PASS Live Pipeline Completed! ID:', recordedRuns['PASS']);
    await recPage.waitForTimeout(3000);

    // 5. Open Verification Workbench
    const openWbBtn1 = recPage.locator('button:has-text("Open Verification Workbench")');
    await moveAndClick(openWbBtn1);
    await recPage.waitForSelector('text=JARVIS_DEMO_PASS_BIDDER', { timeout: 15000 });
    await recPage.getByText('Loading verification dossier...').waitFor({ state: 'hidden', timeout: 15000 }).catch(() => {});
    await recPage.waitForTimeout(3000);

    // 6. Inspect Bidder Turnover Grounding (₹145 Lakhs vs >= ₹100 Lakhs, Page 2 BBox)
    const pTurnover = recPage.locator('tr:has-text("REQ-TENDER-0001-004")').first();
    if (await pTurnover.count() > 0) {
      await moveAndClick(pTurnover);
    } else {
      await moveAndClick(recPage.locator('tr:has-text("145.00")').first());
    }
    await recPage.waitForTimeout(3500);

    // 7. Inspect OEM Turnover Grounding (₹1,050 Lakhs vs >= ₹800 Lakhs)
    const pOem = recPage.locator('tr:has-text("REQ-TENDER-0001-005")').first();
    if (await pOem.count() > 0) {
      await moveAndClick(pOem);
    }
    await recPage.waitForTimeout(3000);

    // Return to Dashboard before Cycle 2
    await goBackToDashboard();
    await recPage.waitForTimeout(2000);

    // =========================================================================
    // PART 1 — CYCLE 2: FAIL BIDDER LIVE PIPELINE EXECUTION
    // =========================================================================
    console.log('>>> [PART 1 - CYCLE 2] FAIL BIDDER RUN');
    const newVerifLink2 = recPage.locator('a[href="/verify/new"]').first();
    await moveAndClick(newVerifLink2);
    await recPage.waitForURL('**/verify/new', { timeout: 8000 });
    await recPage.waitForTimeout(1500);

    // 1. Upload Tender PDF
    console.log('Uploading Tender PDF...');
    const tenderInput2 = recPage.locator('label:has-text("Browse PDF") input[type="file"]');
    await tenderInput2.setInputFiles('D:\\smart_india_hackathon\\project\\video_pdf.pdf');
    await recPage.waitForSelector('text=PDF accepted', { timeout: 10000 });
    await recPage.waitForTimeout(800);

    // 2. Upload FAIL Bidder PDF
    console.log('Uploading FAIL Bidder PDF...');
    const bidInput2 = recPage.locator('label:has-text("Browse files") input[type="file"]');
    await bidInput2.setInputFiles('D:\\smart_india_hackathon\\project\\JARVIS_DEMO_FAIL_BIDDER_GEM_2026_B_7959150.pdf');
    await recPage.waitForSelector('span:has-text("1 file")', { timeout: 10000 });
    await recPage.waitForSelector('text=JARVIS_DEMO_FAIL_BIDDER_GEM_2026_B_7959150.pdf', { timeout: 10000 });
    await recPage.waitForTimeout(1200);

    // 3. Move cursor to Run Verification Pipeline button and trigger
    console.log('Triggering FAIL live verification pipeline...');
    const runBtn2 = recPage.locator('button:has-text("Run verification pipeline")');
    await moveAndClick(runBtn2);

    // 4. Visibly observe 6-stage live execution progression
    await recPage.waitForSelector('text=Verification Complete', { timeout: 45000 });
    const failVerifId = await recPage.locator('span:has-text("ID: VERIF-")').textContent();
    recordedRuns['FAIL'] = failVerifId.trim();
    console.log('FAIL Live Pipeline Completed! ID:', recordedRuns['FAIL']);
    await recPage.waitForTimeout(3000);

    // 5. Open Verification Workbench
    const openWbBtn2 = recPage.locator('button:has-text("Open Verification Workbench")');
    await moveAndClick(openWbBtn2);
    await recPage.waitForSelector('text=JARVIS_DEMO_FAIL_BIDDER', { timeout: 15000 });
    await recPage.getByText('Loading verification dossier...').waitFor({ state: 'hidden', timeout: 15000 }).catch(() => {});
    await recPage.waitForTimeout(3000);

    // 6. Inspect Turnover Shortfall (41.67L < 100L)
    const fTurnover = recPage.locator('tr:has-text("REQ-TENDER-0001-004")').first();
    if (await fTurnover.count() > 0) {
      await moveAndClick(fTurnover);
      await recPage.waitForTimeout(3000);
    }

    // 7. Inspect Experience Shortfall (1.5Y < 3Y)
    const fExp = recPage.locator('tr:has-text("REQ-TENDER-0001-006")').first();
    if (await fExp.count() > 0) {
      await moveAndClick(fExp);
      await recPage.waitForTimeout(3000);
    }

    // 8. Inspect Past Performance Shortfall (120 units < 400 units)
    const fPerf = recPage.locator('tr:has-text("REQ-TENDER-0001-007")').first();
    if (await fPerf.count() > 0) {
      await moveAndClick(fPerf);
      await recPage.waitForTimeout(3000);
    }

    // Return to Dashboard before Cycle 3
    await goBackToDashboard();
    await recPage.waitForTimeout(2000);

    // =========================================================================
    // PART 1 — CYCLE 3: FORENSIC BIDDER LIVE PIPELINE EXECUTION
    // =========================================================================
    console.log('>>> [PART 1 - CYCLE 3] FORENSIC BIDDER RUN');
    const newVerifLink3 = recPage.locator('a[href="/verify/new"]').first();
    await moveAndClick(newVerifLink3);
    await recPage.waitForURL('**/verify/new', { timeout: 8000 });
    await recPage.waitForTimeout(1500);

    // 1. Upload Tender PDF
    console.log('Uploading Tender PDF...');
    const tenderInput3 = recPage.locator('label:has-text("Browse PDF") input[type="file"]');
    await tenderInput3.setInputFiles('D:\\smart_india_hackathon\\project\\video_pdf.pdf');
    await recPage.waitForSelector('text=PDF accepted', { timeout: 10000 });
    await recPage.waitForTimeout(800);

    // 2. Upload FORENSIC Bidder PDF
    console.log('Uploading FORENSIC Bidder PDF...');
    const bidInput3 = recPage.locator('label:has-text("Browse files") input[type="file"]');
    await bidInput3.setInputFiles('D:\\smart_india_hackathon\\project\\JARVIS_DEMO_FORENSIC_BIDDER_GEM_2026_B_7959150.pdf');
    await recPage.waitForSelector('span:has-text("1 file")', { timeout: 10000 });
    await recPage.waitForSelector('text=JARVIS_DEMO_FORENSIC_BIDDER_GEM_2026_B_7959150.pdf', { timeout: 10000 });
    await recPage.waitForTimeout(1200);

    // 3. Move cursor to Run Verification Pipeline button and trigger
    console.log('Triggering FORENSIC live verification pipeline...');
    const runBtn3 = recPage.locator('button:has-text("Run verification pipeline")');
    await moveAndClick(runBtn3);

    // 4. Visibly observe 6-stage live execution progression (noting Step 5: Contradictions)
    await recPage.waitForSelector('text=Verification Complete', { timeout: 45000 });
    const forVerifId = await recPage.locator('span:has-text("ID: VERIF-")').textContent();
    recordedRuns['FORENSIC'] = forVerifId.trim();
    console.log('FORENSIC Live Pipeline Completed! ID:', recordedRuns['FORENSIC']);
    await recPage.waitForTimeout(3000);

    // 5. Open Verification Workbench
    const openWbBtn3 = recPage.locator('button:has-text("Open Verification Workbench")');
    await moveAndClick(openWbBtn3);
    await recPage.waitForSelector('text=JARVIS_DEMO_FORENSIC_BIDDER', { timeout: 15000 });
    await recPage.getByText('Loading verification dossier...').waitFor({ state: 'hidden', timeout: 15000 }).catch(() => {});
    await recPage.waitForTimeout(3000);

    // 6. Open Registries & Contradictions Tab
    console.log('Navigating to Registries & Contradictions tab...');
    const contraTab = recPage.locator('button:has-text("Registries & Contradictions")').first();
    await moveAndClick(contraTab);
    await recPage.waitForTimeout(2500);

    // 7. Inspect Contradiction 1: Turnover Contradiction (Declared ₹145L vs Audited P&L ₹41.67L)
    const turnoverContra = recPage.locator('h4:has-text("Turnover contradiction"), h4:has-text("Turnover Contradiction")').first();
    if (await turnoverContra.count() > 0) {
      await movePointerTo(turnoverContra);
      await turnoverContra.scrollIntoViewIfNeeded();
      await recPage.waitForTimeout(4000);
    } else {
      await recPage.evaluate(() => window.scrollBy({ top: 250, behavior: 'smooth' }));
      await recPage.waitForTimeout(3500);
    }

    // 8. Inspect Contradiction 2: Past Performance Contradiction (Declared 450 units vs Challan 120 units)
    const pastContra = recPage.locator('h4:has-text("Past performance contradiction"), h4:has-text("Past Performance Contradiction")').first();
    if (await pastContra.count() > 0) {
      await movePointerTo(pastContra);
      await pastContra.scrollIntoViewIfNeeded();
      await recPage.waitForTimeout(4000);
    } else {
      await recPage.evaluate(() => window.scrollBy({ top: 300, behavior: 'smooth' }));
      await recPage.waitForTimeout(3500);
    }

    // 9. Navigate to Officer Review Queue (/review)
    console.log('Navigating to Officer Review Queue from forensic finding...');
    const routeBtn = recPage.locator('button:has-text("Route to Review")').first();
    if (await routeBtn.count() > 0 && await routeBtn.isVisible()) {
      await moveAndClick(routeBtn);
    } else {
      await recPage.goto('http://localhost:5173/review', { waitUntil: 'networkidle' });
    }
    await recPage.waitForTimeout(4000);

    // =========================================================================
    // PART 2 — COMPLETE CONSOLIDATED WEBSITE TOUR
    // =========================================================================
    console.log('>>> [PART 2] CONSOLIDATED COMPLETE WEBSITE TOUR');

    // TOUR 1 & 2: PROCUREMENT DASHBOARD & RECENT ACTIVITY
    console.log('Tour 1 & 2: Dashboard Overview & Recent Activity');
    await recPage.goto('http://localhost:5173/dashboard', { waitUntil: 'networkidle' });
    await recPage.waitForTimeout(2500);

    // Showcase Verification Pulse metrics
    const pulseSection = recPage.locator('div:has-text("Verification Pulse")').first();
    if (await pulseSection.count() > 0) {
      await movePointerTo(pulseSection);
      await recPage.waitForTimeout(2000);
    }

    // Smoothly scroll down to Recent Verification Activity
    await recPage.evaluate(() => window.scrollBy({ top: 380, behavior: 'smooth' }));
    await recPage.waitForTimeout(4000);

    // TOUR 3: NEW VERIFICATION DOCUMENT INTAKE INTERFACE
    console.log('Tour 3: New Verification Intake Interface');
    await recPage.goto('http://localhost:5173/verify/new', { waitUntil: 'networkidle' });
    await recPage.waitForTimeout(2500);
    // Move cursor over Tender panel then Bidder panel
    const tenderBox = recPage.locator('h2:has-text("Tender Specification")').first();
    if (await tenderBox.count() > 0) await movePointerTo(tenderBox);
    await recPage.waitForTimeout(1500);
    const bidderBox = recPage.locator('h2:has-text("Bidder Submissions")').first();
    if (await bidderBox.count() > 0) await movePointerTo(bidderBox);
    await recPage.waitForTimeout(2000);

    // TOUR 4, 5, 6, 7: VERIFICATION WORKBENCH, MATRIX, EXPLAINABILITY, PROCESS & POLICY
    console.log('Tour 4-7: Verification Workbench, Matrix, Explainability, Process & Policy');
    // Open the completed PASS verification workbench
    await recPage.goto(`http://localhost:5173/verification/${recordedRuns['PASS'] ? recordedRuns['PASS'].replace('ID: ', '') : 'VERIF-TENDER-0001-JARVIS_DEMO_PASS_BIDDER'}`, { waitUntil: 'networkidle' });
    await recPage.getByText('Loading verification dossier...').waitFor({ state: 'hidden', timeout: 15000 }).catch(() => {});
    await recPage.waitForTimeout(2500);

    // Tour 4: Global Command Bar & Analytical Summary Rail
    const commandBar = recPage.locator('h1').first();
    await movePointerTo(commandBar);
    await recPage.waitForTimeout(1500);

    // Tour 5 & 6: Document & Matrix with Physical Evidence Grounding
    const tourTurnover = recPage.locator('tr:has-text("REQ-TENDER-0001-004")').first();
    if (await tourTurnover.count() > 0) {
      await moveAndClick(tourTurnover);
      await recPage.waitForTimeout(3000);
    }

    // Tour 7: Process & Policy Scope Tab
    console.log('Tour 7: Process & Policy Condition Filtering');
    const processTab = recPage.locator('button:has-text("Process & Policy")').first();
    if (await processTab.count() > 0) {
      await moveAndClick(processTab);
      await recPage.waitForTimeout(2500);
      // Switch back to Obligations tab
      const obligationsTab = recPage.locator('button:has-text("Obligations")').first();
      await moveAndClick(obligationsTab);
      await recPage.waitForTimeout(2000);
    }

    // TOUR 8: REGISTRIES & CONTRADICTIONS INTERFACE
    console.log('Tour 8: Registries & Contradictions on Forensic Run');
    await recPage.goto(`http://localhost:5173/verification/${recordedRuns['FORENSIC'] ? recordedRuns['FORENSIC'].replace('ID: ', '') : 'VERIF-TENDER-0001-JARVIS_DEMO_FORENSIC_BIDDER'}`, { waitUntil: 'networkidle' });
    await recPage.getByText('Loading verification dossier...').waitFor({ state: 'hidden', timeout: 15000 }).catch(() => {});
    await recPage.waitForTimeout(2000);
    const tourContraTab = recPage.locator('button:has-text("Registries & Contradictions")').first();
    await moveAndClick(tourContraTab);
    await recPage.waitForTimeout(3000);

    // TOUR 9: OFFICER REVIEW QUEUE WORKFLOW
    console.log('Tour 9: Officer Review Queue Workflow');
    await recPage.goto('http://localhost:5173/review', { waitUntil: 'networkidle' });
    await recPage.waitForTimeout(2500);
    // Point to review row to show details
    const firstReviewRow = recPage.locator('table tbody tr').first();
    if (await firstReviewRow.count() > 0) {
      await moveAndClick(firstReviewRow);
      await recPage.waitForTimeout(2500);
    }

    // TOUR 10: AUDIT DOSSIER JSON
    console.log('Tour 10: Audit Dossier JSON View');
    await recPage.goto(`http://localhost:5173/verification/${recordedRuns['PASS'] ? recordedRuns['PASS'].replace('ID: ', '') : 'VERIF-TENDER-0001-JARVIS_DEMO_PASS_BIDDER'}`, { waitUntil: 'networkidle' });
    await recPage.getByText('Loading verification dossier...').waitFor({ state: 'hidden', timeout: 15000 }).catch(() => {});
    await recPage.waitForTimeout(2000);
    const dossierTab = recPage.locator('button:has-text("Dossier JSON")').first();
    if (await dossierTab.count() > 0) {
      await moveAndClick(dossierTab);
      await recPage.waitForTimeout(3000);
      // Switch back to Document & Matrix
      const matrixTab = recPage.locator('button:has-text("Document & Matrix")').first();
      await moveAndClick(matrixTab);
      await recPage.waitForTimeout(1500);
    }

    // TOUR 11 & CLOSING SHOT: FINAL DASHBOARD
    console.log('Tour 11 & Closing Shot: Procurement Dashboard Recent Activity');
    await recPage.goto('http://localhost:5173/dashboard', { waitUntil: 'networkidle' });
    await recPage.waitForTimeout(2000);
    await recPage.evaluate(() => window.scrollBy({ top: 380, behavior: 'smooth' }));
    await recPage.waitForTimeout(1500);

    // Place cursor calmly in the header region of Recent Activity
    const recentHeading = recPage.locator('h3:has-text("Recent Verification Activity"), h2:has-text("Recent Verification Activity")').first();
    if (await recentHeading.count() > 0) {
      await movePointerTo(recentHeading);
    } else {
      await recPage.mouse.move(720, 260, { steps: 8 });
    }

    // Hold final dashboard shot for ~7 seconds
    console.log('Holding final dashboard closing shot for 7 seconds...');
    await recPage.waitForTimeout(7000);

    console.log('>>> COMPLETE DEMONSTRATION RECORDED SUCCESSFULLY!');
  } finally {
    const video = recPage.video();
    await recPage.close();
    await context.close();

    if (video) {
      await video.saveAs(finalVideoPath);
      console.log('Saved final demonstration video to:', finalVideoPath);
    }
  }

  return {
    finalVideoPath,
    recordedRuns,
    status: 'COMPLETE_DEMO_RECORDED_SUCCESSFULLY'
  };
}
