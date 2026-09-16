// record_final_complete_demo.js - J.A.R.V.I.S Complete Video Demonstration
// PART 1: Three Live Pipeline Verifications (PASS, FAIL, FORENSIC) with fresh execution and Workbench inspection
// PART 2: Consolidated Complete Website Tour (Dashboard, Intake, Workbench, Matrix, Explainability, Process/Policy, Contradictions, Review Queue, Investigate, Decide, Officer Note, Audit Dossier, Closing Shot)
// Guaranteed cursor synchronization: visual cursor overlay glides frame-by-frame, reaches button, pauses, pulses, and then triggers click.

async (page) => {
  const browser = page.context().browser();
  const videoDir = 'D:\\smart_india_hackathon\\project';
  const finalVideoPath = 'D:\\smart_india_hackathon\\project\\JARVIS_FINAL_COMPLETE_DEMO.webm';

  // Create isolated context with video recording at 1440x900 viewport
  const context = await browser.newContext({
    recordVideo: {
      dir: videoDir,
      size: { width: 1440, height: 900 }
    },
    viewport: { width: 1440, height: 900 }
  });

  // Inject synchronized cursor controller directly into window
  await context.addInitScript(() => {
    window.__cursorX = 720;
    window.__cursorY = 450;

    const setupCursor = () => {
      if (document.getElementById('playwright-custom-cursor')) return;

      const cursorContainer = document.createElement('div');
      cursorContainer.id = 'playwright-custom-cursor';
      cursorContainer.style.cssText = 'position:fixed;top:0;left:0;width:0;height:0;z-index:999999999;pointer-events:none;';

      const cursor = document.createElement('div');
      cursor.id = 'cursor-pointer-icon';
      cursor.style.cssText = `position:absolute;width:24px;height:24px;left:${window.__cursorX}px;top:${window.__cursorY}px;transform:translate(-2px,-2px);pointer-events:none;will-change:left,top;`;
      cursor.innerHTML = `
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter:drop-shadow(0 2px 5px rgba(0,0,0,0.65));">
          <path d="M4 3L11.5 21L14.5 13.5L22 10.5L4 3Z" fill="#1D4ED8" stroke="#FFFFFF" stroke-width="2.2" stroke-linejoin="round"/>
        </svg>
      `;

      const clickRipple = document.createElement('div');
      clickRipple.id = 'cursor-click-ripple';
      clickRipple.style.cssText = `position:absolute;width:34px;height:34px;left:${window.__cursorX}px;top:${window.__cursorY}px;border-radius:50%;border:2.5px solid #2563EB;background:rgba(37,99,235,0.25);transform:translate(-17px,-17px) scale(0);opacity:0;pointer-events:none;`;

      cursorContainer.appendChild(clickRipple);
      cursorContainer.appendChild(cursor);
      document.body.appendChild(cursorContainer);
    };

    window.__moveCursorTo = (targetX, targetY, durationMs = 260) => {
      return new Promise((resolve) => {
        setupCursor();
        const cursor = document.getElementById('cursor-pointer-icon');
        const clickRipple = document.getElementById('cursor-click-ripple');
        if (!cursor) {
          window.__cursorX = targetX;
          window.__cursorY = targetY;
          return resolve();
        }

        const startX = window.__cursorX;
        const startY = window.__cursorY;
        const startTime = performance.now();

        const step = (now) => {
          const elapsed = now - startTime;
          const progress = Math.min(elapsed / durationMs, 1);
          // Ease-out cubic
          const ease = 1 - Math.pow(1 - progress, 3);
          const currentX = Math.round(startX + (targetX - startX) * ease);
          const currentY = Math.round(startY + (targetY - startY) * ease);

          cursor.style.left = `${currentX}px`;
          cursor.style.top = `${currentY}px`;
          if (clickRipple) {
            clickRipple.style.left = `${currentX}px`;
            clickRipple.style.top = `${currentY}px`;
          }

          if (progress < 1) {
            requestAnimationFrame(step);
          } else {
            window.__cursorX = targetX;
            window.__cursorY = targetY;
            resolve();
          }
        };

        requestAnimationFrame(step);
      });
    };

    window.__clickCursor = () => {
      return new Promise((resolve) => {
        const cursor = document.getElementById('cursor-pointer-icon');
        const clickRipple = document.getElementById('cursor-click-ripple');
        if (cursor) cursor.style.transform = 'translate(-2px,-2px) scale(0.85)';
        if (clickRipple) {
          clickRipple.style.transform = 'translate(-17px,-17px) scale(1.15)';
          clickRipple.style.opacity = '1';
        }
        setTimeout(() => {
          if (cursor) cursor.style.transform = 'translate(-2px,-2px) scale(1)';
          if (clickRipple) {
            clickRipple.style.transform = 'translate(-17px,-17px) scale(1.6)';
            clickRipple.style.opacity = '0';
          }
          resolve();
        }, 110);
      });
    };

    window.addEventListener('DOMContentLoaded', setupCursor);
  });

  const recPage = await context.newPage();

  // Deterministic synchronized movement & click helpers
  const glideCursor = async (targetX, targetY, durationMs = 260) => {
    await recPage.evaluate(async ({ x, y, duration }) => {
      await window.__moveCursorTo(x, y, duration);
    }, { x: targetX, y: targetY, duration: durationMs });
    await recPage.waitForTimeout(60);
  };

  const pointAt = async (locator, durationMs = 260) => {
    try {
      await locator.scrollIntoViewIfNeeded();
      await recPage.waitForTimeout(80);
      const box = await locator.boundingBox();
      if (box) {
        const targetX = Math.round(box.x + box.width / 2);
        const targetY = Math.round(box.y + box.height / 2);
        await glideCursor(targetX, targetY, durationMs);
        await recPage.waitForTimeout(150);
      }
    } catch (e) {}
  };

  const moveAndClick = async (locator, options = {}) => {
    try {
      await locator.scrollIntoViewIfNeeded();
      await recPage.waitForTimeout(80);
      const box = await locator.boundingBox();
      if (box) {
        const targetX = Math.round(box.x + box.width / 2);
        const targetY = Math.round(box.y + box.height / 2);
        // 1. Move cursor visually to target BEFORE click
        await glideCursor(targetX, targetY, 260);
        // 2. Pause with cursor visibly resting on target
        await recPage.waitForTimeout(120);
        // 3. Visual click pulse
        await recPage.evaluate(() => window.__clickCursor());
        await recPage.waitForTimeout(60);
      }
      // 4. Trigger actual click
      await locator.click(options);
      await recPage.waitForTimeout(250);
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
    // =========================================================================
    // PART 1 — CYCLE 1: PASS BIDDER LIVE PIPELINE EXECUTION
    // =========================================================================
    console.log('>>> [PART 1 - CYCLE 1] PASS BIDDER RUN');
    await recPage.goto('http://localhost:5173/dashboard', { waitUntil: 'networkidle' });
    await recPage.waitForTimeout(1500);

    // Navigate to New Bid Verification
    const newVerifLink1 = recPage.locator('a[href="/verify/new"]').first();
    await moveAndClick(newVerifLink1);
    await recPage.waitForURL('**/verify/new', { timeout: 8000 });
    await recPage.waitForTimeout(1200);

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
    await recPage.waitForTimeout(1000);

    // 3. Move cursor to Run Verification Pipeline button, pause, click
    console.log('Triggering PASS live verification pipeline...');
    const runBtn1 = recPage.locator('button:has-text("Run verification pipeline")');
    await moveAndClick(runBtn1);

    // 4. Visibly observe 6-stage live execution progression ONCE
    await recPage.waitForSelector('text=Verification Complete', { timeout: 45000 });
    const passVerifId = await recPage.locator('span:has-text("ID: VERIF-")').textContent();
    recordedRuns['PASS'] = passVerifId.trim();
    console.log('PASS Live Pipeline Completed! ID:', recordedRuns['PASS']);
    await recPage.waitForTimeout(2500);

    // 5. Open Verification Workbench
    const openWbBtn1 = recPage.locator('button:has-text("Open Verification Workbench")');
    await moveAndClick(openWbBtn1);
    await recPage.waitForSelector('text=JARVIS_DEMO_PASS_BIDDER', { timeout: 15000 });
    await recPage.getByText('Loading verification dossier...').waitFor({ state: 'hidden', timeout: 15000 }).catch(() => {});
    await recPage.waitForTimeout(2500);

    // 6. Inspect Bidder Turnover Grounding (₹145 Lakhs vs >= ₹100 Lakhs, Page 2 BBox)
    const pTurnover = recPage.locator('tr:has-text("REQ-TENDER-0001-004")').first();
    if (await pTurnover.count() > 0) {
      await moveAndClick(pTurnover);
    } else {
      await moveAndClick(recPage.locator('tr:has-text("145.00")').first());
    }
    await recPage.waitForTimeout(3000);

    // 7. Inspect OEM Turnover Grounding (₹1,050 Lakhs vs >= ₹800 Lakhs)
    const pOem = recPage.locator('tr:has-text("REQ-TENDER-0001-005")').first();
    if (await pOem.count() > 0) {
      await moveAndClick(pOem);
    }
    await recPage.waitForTimeout(2500);

    // Return to Dashboard before Cycle 2
    await goBackToDashboard();
    await recPage.waitForTimeout(1500);

    // =========================================================================
    // PART 1 — CYCLE 2: FAIL BIDDER LIVE PIPELINE EXECUTION
    // =========================================================================
    console.log('>>> [PART 1 - CYCLE 2] FAIL BIDDER RUN');
    const newVerifLink2 = recPage.locator('a[href="/verify/new"]').first();
    await moveAndClick(newVerifLink2);
    await recPage.waitForURL('**/verify/new', { timeout: 8000 });
    await recPage.waitForTimeout(1200);

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
    await recPage.waitForTimeout(1000);

    // 3. Move cursor to Run Verification Pipeline button, pause, click
    console.log('Triggering FAIL live verification pipeline...');
    const runBtn2 = recPage.locator('button:has-text("Run verification pipeline")');
    await moveAndClick(runBtn2);

    // 4. Visibly observe 6-stage live execution progression ONCE
    await recPage.waitForSelector('text=Verification Complete', { timeout: 45000 });
    const failVerifId = await recPage.locator('span:has-text("ID: VERIF-")').textContent();
    recordedRuns['FAIL'] = failVerifId.trim();
    console.log('FAIL Live Pipeline Completed! ID:', recordedRuns['FAIL']);
    await recPage.waitForTimeout(2500);

    // 5. Open Verification Workbench
    const openWbBtn2 = recPage.locator('button:has-text("Open Verification Workbench")');
    await moveAndClick(openWbBtn2);
    await recPage.waitForSelector('text=JARVIS_DEMO_FAIL_BIDDER', { timeout: 15000 });
    await recPage.getByText('Loading verification dossier...').waitFor({ state: 'hidden', timeout: 15000 }).catch(() => {});
    await recPage.waitForTimeout(2500);

    // 6. Highlight real shortfalls: Turnover (41.67L < 100L) with BBox
    const fTurnover = recPage.locator('tr:has-text("REQ-TENDER-0001-004")').first();
    if (await fTurnover.count() > 0) {
      await moveAndClick(fTurnover);
      await recPage.waitForTimeout(2500);
    }

    // 7. Highlight Experience Shortfall (1.5Y < 3Y)
    const fExp = recPage.locator('tr:has-text("REQ-TENDER-0001-006")').first();
    if (await fExp.count() > 0) {
      await moveAndClick(fExp);
      await recPage.waitForTimeout(2500);
    }

    // 8. Highlight Past Performance Shortfall (120 units < 400 units)
    const fPerf = recPage.locator('tr:has-text("REQ-TENDER-0001-007")').first();
    if (await fPerf.count() > 0) {
      await moveAndClick(fPerf);
      await recPage.waitForTimeout(2500);
    }

    // Return to Dashboard before Cycle 3
    await goBackToDashboard();
    await recPage.waitForTimeout(1500);

    // =========================================================================
    // PART 1 — CYCLE 3: FORENSIC BIDDER LIVE PIPELINE EXECUTION
    // =========================================================================
    console.log('>>> [PART 1 - CYCLE 3] FORENSIC BIDDER RUN');
    const newVerifLink3 = recPage.locator('a[href="/verify/new"]').first();
    await moveAndClick(newVerifLink3);
    await recPage.waitForURL('**/verify/new', { timeout: 8000 });
    await recPage.waitForTimeout(1200);

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
    await recPage.waitForTimeout(1000);

    // 3. Move cursor to Run Verification Pipeline button, pause, click
    console.log('Triggering FORENSIC live verification pipeline...');
    const runBtn3 = recPage.locator('button:has-text("Run verification pipeline")');
    await moveAndClick(runBtn3);

    // 4. Visibly observe 6-stage live execution progression ONCE (noting Step 5: Contradictions)
    await recPage.waitForSelector('text=Verification Complete', { timeout: 45000 });
    const forVerifId = await recPage.locator('span:has-text("ID: VERIF-")').textContent();
    recordedRuns['FORENSIC'] = forVerifId.trim();
    console.log('FORENSIC Live Pipeline Completed! ID:', recordedRuns['FORENSIC']);
    await recPage.waitForTimeout(2500);

    // 5. Open Verification Workbench
    const openWbBtn3 = recPage.locator('button:has-text("Open Verification Workbench")');
    await moveAndClick(openWbBtn3);
    await recPage.waitForSelector('text=JARVIS_DEMO_FORENSIC_BIDDER', { timeout: 15000 });
    await recPage.getByText('Loading verification dossier...').waitFor({ state: 'hidden', timeout: 15000 }).catch(() => {});
    await recPage.waitForTimeout(2500);

    // 6. Open Registries & Contradictions Tab
    console.log('Navigating to Registries & Contradictions tab...');
    const contraTab = recPage.locator('button:has-text("Registries & Contradictions")').first();
    await moveAndClick(contraTab);
    await recPage.waitForTimeout(2000);

    // 7. Inspect Contradiction 1: Turnover Contradiction (Declared ₹145L vs Audited P&L ₹41.67L)
    const turnoverContra = recPage.locator('h4:has-text("Turnover contradiction"), h4:has-text("Turnover Contradiction")').first();
    if (await turnoverContra.count() > 0) {
      await pointAt(turnoverContra);
      await turnoverContra.scrollIntoViewIfNeeded();
      await recPage.waitForTimeout(3500);
    }

    // 8. Inspect Contradiction 2: Past Performance Contradiction (Declared 450 units vs Challan 120 units)
    const pastContra = recPage.locator('h4:has-text("Past performance contradiction"), h4:has-text("Past Performance Contradiction")').first();
    if (await pastContra.count() > 0) {
      await pointAt(pastContra);
      await pastContra.scrollIntoViewIfNeeded();
      await recPage.waitForTimeout(3500);
    }

    // =========================================================================
    // PART 2 — CONSOLIDATED COMPLETE WEBSITE TOUR
    // (Features shown once; no repeated pipelines)
    // =========================================================================
    console.log('>>> [PART 2] CONSOLIDATED COMPLETE WEBSITE TOUR');

    // TOUR 1 & 2: PROCUREMENT DASHBOARD & RECENT ACTIVITY
    console.log('Tour 1 & 2: Dashboard Command Center & Recent Verification Activity');
    await recPage.goto('http://localhost:5173/dashboard', { waitUntil: 'networkidle' });
    await recPage.waitForTimeout(2000);

    // Showcase Verification Pulse metrics at top
    const pulseHeader = recPage.locator('h2:has-text("Verification Pulse"), div:has-text("Verification Pulse")').first();
    if (await pulseHeader.count() > 0) {
      await pointAt(pulseHeader);
      await recPage.waitForTimeout(1800);
    }

    // Deliberately scroll down to Recent Verification Activity table
    await recPage.evaluate(() => window.scrollBy({ top: 380, behavior: 'smooth' }));
    await recPage.waitForTimeout(2000);
    const recentTableHeading = recPage.locator('h3:has-text("Recent Verification Activity"), h2:has-text("Recent Verification Activity")').first();
    if (await recentTableHeading.count() > 0) {
      await pointAt(recentTableHeading);
      await recPage.waitForTimeout(3000);
    }

    // TOUR 2: LEFT SIDEBAR / CURVED NAVIGATION MENU
    console.log('Tour 2: Left Curved Navigation Menu');
    const menuBtn = recPage.locator('button:has-text("Menu"), div[title="Open menu"], button[aria-label="Open menu"]').first();
    if (await menuBtn.count() > 0) {
      await moveAndClick(menuBtn);
      await recPage.waitForTimeout(2000);
      // Close menu
      await moveAndClick(menuBtn);
      await recPage.waitForTimeout(1000);
    }

    // TOUR 3: NEW VERIFICATION DOCUMENT INTAKE INTERFACE
    console.log('Tour 3: New Verification Document Submission Interface');
    await recPage.goto('http://localhost:5173/verify/new', { waitUntil: 'networkidle' });
    await recPage.waitForTimeout(2000);
    const tenderSection = recPage.locator('h2:has-text("Tender Specification")').first();
    if (await tenderSection.count() > 0) await pointAt(tenderSection);
    await recPage.waitForTimeout(1200);
    const bidderSection = recPage.locator('h2:has-text("Bidder Submissions")').first();
    if (await bidderSection.count() > 0) await pointAt(bidderSection);
    await recPage.waitForTimeout(1500);

    // TOUR 4: VERIFICATION WORKBENCH OVERVIEW & ANALYTICAL RAIL
    console.log('Tour 4: Verification Workbench Structural Overview');
    await recPage.goto(`http://localhost:5173/verification/${recordedRuns['PASS'] ? recordedRuns['PASS'].replace('ID: ', '') : 'VERIF-TENDER-0001-JARVIS_DEMO_PASS_BIDDER'}`, { waitUntil: 'networkidle' });
    await recPage.getByText('Loading verification dossier...').waitFor({ state: 'hidden', timeout: 15000 }).catch(() => {});
    await recPage.waitForTimeout(2000);

    // Point to global summary bar and score
    const scoreGauge = recPage.locator('span:has-text("SCORE:")').first();
    if (await scoreGauge.count() > 0) await pointAt(scoreGauge);
    await recPage.waitForTimeout(1200);

    // TOUR 5 & 6: DOCUMENT & MATRIX + PHYSICAL EVIDENCE EXPLAINABILITY
    console.log('Tour 5 & 6: Document & Matrix with Physical Evidence Grounding');
    const matrixRow = recPage.locator('tr:has-text("REQ-TENDER-0001-004")').first();
    if (await matrixRow.count() > 0) {
      await moveAndClick(matrixRow);
      await recPage.waitForTimeout(2500);
    }

    // TOUR 7: PROCESS & POLICY CONDITION FILTERING
    console.log('Tour 7: Process & Policy Condition Filtering');
    const processTab = recPage.locator('button:has-text("Process & Policy")').first();
    if (await processTab.count() > 0) {
      await moveAndClick(processTab);
      await recPage.waitForTimeout(2500);
      // Switch back to Obligations tab
      const obligationsTab = recPage.locator('button:has-text("Obligations")').first();
      await moveAndClick(obligationsTab);
      await recPage.waitForTimeout(1800);
    }

    // TOUR 8: DEDICATED REGISTRIES & CONTRADICTIONS INTERFACE
    console.log('Tour 8: Registries & Contradictions Structural View');
    await recPage.goto(`http://localhost:5173/verification/${recordedRuns['FORENSIC'] ? recordedRuns['FORENSIC'].replace('ID: ', '') : 'VERIF-TENDER-0001-JARVIS_DEMO_FORENSIC_BIDDER'}`, { waitUntil: 'networkidle' });
    await recPage.getByText('Loading verification dossier...').waitFor({ state: 'hidden', timeout: 15000 }).catch(() => {});
    await recPage.waitForTimeout(1800);
    const wbContraTab = recPage.locator('button:has-text("Registries & Contradictions")').first();
    await moveAndClick(wbContraTab);
    await recPage.waitForTimeout(2500);

    // TOUR 5, 6, 7, 8: OFFICER REVIEW QUEUE, INVESTIGATE, DECIDE, OFFICER NOTE
    console.log('Tour 5-8: Officer Review Queue, Investigate, Decide, Officer Note');
    await recPage.goto('http://localhost:5173/review', { waitUntil: 'networkidle' });
    await recPage.waitForTimeout(2500);

    // Tour 6: Point to "Investigate" link
    const investigateLink = recPage.locator('a:has-text("Investigate")').first();
    if (await investigateLink.count() > 0) {
      await pointAt(investigateLink);
      await recPage.waitForTimeout(1500);
    }

    // Tour 7: Click "Decide" button to open Adjudication workflow
    const decideBtn = recPage.locator('button:has-text("Decide")').first();
    if (await decideBtn.count() > 0) {
      await moveAndClick(decideBtn);
      await recPage.waitForTimeout(2500);

      // Tour 7: Point to Decision options (Confirm, Dismiss, Clarification)
      const confirmOpt = recPage.locator('button:has-text("Confirm discrepancy")').first();
      if (await confirmOpt.count() > 0) {
        await pointAt(confirmOpt);
        await recPage.waitForTimeout(1500);
      }

      // Tour 8: Point to Officer Note textarea
      const noteField = recPage.locator('textarea[placeholder*="reasoning"]').first();
      if (await noteField.count() > 0) {
        await pointAt(noteField);
        await recPage.waitForTimeout(1800);
      }

      // Close modal gracefully without destructive action
      const cancelBtn = recPage.locator('button:has-text("Cancel"), button[aria-label="Close adjudication"]').first();
      if (await cancelBtn.count() > 0) {
        await moveAndClick(cancelBtn);
        await recPage.waitForTimeout(1200);
      }
    }

    // TOUR 10: AUDIT DOSSIER JSON
    console.log('Tour 10: Structured Audit Dossier JSON Record');
    await recPage.goto(`http://localhost:5173/verification/${recordedRuns['PASS'] ? recordedRuns['PASS'].replace('ID: ', '') : 'VERIF-TENDER-0001-JARVIS_DEMO_PASS_BIDDER'}`, { waitUntil: 'networkidle' });
    await recPage.getByText('Loading verification dossier...').waitFor({ state: 'hidden', timeout: 15000 }).catch(() => {});
    await recPage.waitForTimeout(1800);

    const dossierTab = recPage.locator('button:has-text("Dossier JSON")').first();
    if (await dossierTab.count() > 0) {
      await moveAndClick(dossierTab);
      await recPage.waitForTimeout(3000);
      // Return to Document & Matrix
      const matrixTab = recPage.locator('button:has-text("Document & Matrix")').first();
      await moveAndClick(matrixTab);
      await recPage.waitForTimeout(1200);
    }

    // TOUR 12: FINAL DASHBOARD CLOSING SHOT
    console.log('Tour 12: Final Dashboard Recent Verification Activity Closing Shot');
    await recPage.goto('http://localhost:5173/dashboard', { waitUntil: 'networkidle' });
    await recPage.waitForTimeout(1800);

    // Smoothly scroll down so Recent Verification Activity is centered
    await recPage.evaluate(() => window.scrollBy({ top: 380, behavior: 'smooth' }));
    await recPage.waitForTimeout(1500);

    // Place cursor calmly over the table header
    const finalRecentHeading = recPage.locator('h3:has-text("Recent Verification Activity"), h2:has-text("Recent Verification Activity")').first();
    if (await finalRecentHeading.count() > 0) {
      await pointAt(finalRecentHeading);
    } else {
      await glideCursor(720, 260, 260);
    }

    // Hold final dashboard shot for ~7 seconds
    console.log('Holding final dashboard shot for 7 seconds...');
    await recPage.waitForTimeout(7000);

    console.log('>>> JARVIS FINAL COMPLETE DEMONSTRATION RECORDED SUCCESSFULLY!');
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
