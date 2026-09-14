import React, { useState, useEffect, useMemo } from "react";
import { useParams, Link, useNavigate, useLocation } from "react-router-dom";
import {
  ArrowLeft,
  ShieldCheck,
  ShieldAlert,
  FileText,
  Clock,
  ExternalLink,
  Download,
  AlertTriangle,
  Building2,
  CheckCircle2,
  Scan,
  CornerDownRight,
  Hash,
  Eye,
  Loader2,
} from "lucide-react";
import {
  CANONICAL_DEMO_CASES,
  SEEDED_DEMO_VERIFICATIONS,
  DEMO_PHYSICAL_TEXT_BLOCKS,
  PhysicalTextBlock,
} from "../data/demoCases";
import {
  ComplianceBadge,
  IntegrityBadge,
  OverallBadge,
  SeverityBadge,
} from "../components/status/StatusBadges";
import { DocumentCanvas } from "../components/evidence/DocumentCanvas";
import {
  EvidenceInspector,
  EvidenceData,
} from "../components/evidence/EvidenceInspector";
import { RequirementMatrixTable } from "../components/matrix/RequirementMatrixTable";
import { AggregatedVerification, VerificationResult } from "../types";
import { apiClient } from "../api/client";

export const VerificationWorkbenchPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const navigate = useNavigate();

  const stateVerification = (location.state as any)?.verification as AggregatedVerification | undefined;

  const [loadedVerification, setLoadedVerification] = useState<AggregatedVerification | null>(() => {
    if (stateVerification && (!id || stateVerification.verification_id === id)) {
      return stateVerification;
    }
    const foundSeeded = SEEDED_DEMO_VERIFICATIONS.find((v) => v.verification_id === id);
    if (foundSeeded) return foundSeeded;
    return null;
  });

  const [loadedDossier, setLoadedDossier] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(!loadedVerification && !!id);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    const seeded = SEEDED_DEMO_VERIFICATIONS.find((v) => v.verification_id === id);
    if (seeded) {
      setLoadedVerification(seeded);
      setIsLoading(false);
      return;
    }

    setIsLoading(!loadedVerification);
    setLoadError(null);

    Promise.all([
      apiClient.getVerification(id).catch((err) => {
        if (loadedVerification) return loadedVerification;
        throw err;
      }),
      apiClient.getDossier(id).catch(() => null),
    ])
      .then(([verifData, dossierData]) => {
        setLoadedVerification(verifData);
        if (dossierData) setLoadedDossier(dossierData);
        setIsLoading(false);

        // Persist loaded verification ID to local storage registry
        if (verifData?.verification_id) {
          try {
            const rawList = localStorage.getItem("jarvis_recent_verifications");
            const existing: string[] = rawList ? JSON.parse(rawList) : [];
            const updated = [verifData.verification_id, ...existing.filter((vid) => vid !== verifData.verification_id)].slice(0, 50);
            localStorage.setItem("jarvis_recent_verifications", JSON.stringify(updated));
          } catch (storageErr) {
            console.warn("Could not persist recent verification ID:", storageErr);
          }
        }
      })
      .catch((err) => {
        console.error("Failed to load verification from backend:", err);
        setLoadError(err.detail || err.message || `Verification '${id}' not found on backend.`);
        setIsLoading(false);
      });
  }, [id]);

  // Isolate seeded demo cases: Real requested verification IDs must NEVER fall back to demoCases[0]
  const verification = loadedVerification || (id ? null : SEEDED_DEMO_VERIFICATIONS[0]);

  const companyName = verification
    ? (CANONICAL_DEMO_CASES.find((c) => c.bid_id === verification.bid_id)?.company_name ||
        (verification.processing_metadata as any)?.legal_name ||
        (verification.processing_metadata as any)?.company_name ||
        verification.bid_id)
    : "";

  const physicalBlocks: (PhysicalTextBlock & { matched_clause_id?: string })[] = useMemo(() => {
    if (!verification) return [];
    const isSeededDemo = SEEDED_DEMO_VERIFICATIONS.some((s) => s.verification_id === verification?.verification_id);
    if (isSeededDemo && DEMO_PHYSICAL_TEXT_BLOCKS[verification.bid_id]) {
      return DEMO_PHYSICAL_TEXT_BLOCKS[verification.bid_id];
    }

    const blocks: (PhysicalTextBlock & { matched_clause_id?: string })[] = [];
    const seenBlockIds = new Set<string>();

    // 1. Gather all genuine evidence directly from verification results
    (verification.verification_results || []).forEach((vr) => {
      (vr.evidence || []).forEach((ev: any, evIdx: number) => {
        const snippet = ev.snippet || ev.raw_text_snippet || ev.text || "";
        if (!snippet.trim()) return;
        const blkId = ev.block_id || `BLK-${vr.requirement_id}-${evIdx}`;
        if (!seenBlockIds.has(blkId)) {
          seenBlockIds.add(blkId);
          blocks.push({
            id: blkId,
            page: ev.page || 1,
            bbox: (ev.bbox as [number, number, number, number]) || [0, 0, 0, 0],
            text: snippet,
            grounding_state: "VERIFIED",
            confidence_heuristic: "HIGH",
            clause_id: vr.requirement_id,
            matched_clause_id: vr.requirement_id,
          });
        }
      });
    });

    // 2. Also check if dossier contains additional facts from bidder extraction
    if (loadedDossier?.bidder?.facts && Array.isArray(loadedDossier.bidder.facts)) {
      loadedDossier.bidder.facts.forEach((fact: any, fIdx: number) => {
        const factSnippet = fact.raw_text_snippet || fact.snippet || String(fact.value || "");
        const evList = (fact.evidence && fact.evidence.length > 0) ? fact.evidence : [{
          page: fact.page || 1,
          bbox: fact.bbox || [0, 0, 0, 0],
          snippet: factSnippet,
        }];
        evList.forEach((ev: any, evIdx: number) => {
          const snippet = ev.snippet || ev.raw_text_snippet || factSnippet;
          if (!snippet.trim()) return;
          const blkId = ev.block_id || `FACT-BLK-${fIdx}-${evIdx}`;
          if (!seenBlockIds.has(blkId)) {
            seenBlockIds.add(blkId);
            blocks.push({
              id: blkId,
              page: ev.page || fact.page || 1,
              bbox: (ev.bbox || fact.bbox || [0, 0, 0, 0]) as [number, number, number, number],
              text: snippet,
              grounding_state: "VERIFIED",
              confidence_heuristic: "HIGH",
              clause_id: fact.field || fact.canonical_field || undefined,
              matched_clause_id: fact.field || fact.canonical_field || undefined,
            });
          }
        });
      });
    }

    return blocks;
  }, [verification, loadedDossier]);

  // Active state
  const [selectedClauseId, setSelectedClauseId] = useState<string | null>(() => {
    if (!verification?.verification_results?.length) return null;
    const firstBidder = verification.verification_results.find(
      (r) => r.status !== "N/A" && r.status !== "N_A"
    );
    return firstBidder?.requirement_id || verification.verification_results[0].requirement_id;
  });
  const [selectedBlockId, setSelectedBlockId] = useState<string | null>(null);
  const [activeEvidence, setActiveEvidence] = useState<EvidenceData | null>(null);
  const [hoveredEvidence, setHoveredEvidence] = useState<EvidenceData | null>(null);
  const [inspectorPos, setInspectorPos] = useState<{ x: number; y: number } | null>(null);
  const [activeWorkspaceTab, setActiveWorkspaceTab] = useState<"forensics" | "registries" | "dossier">(
    verification?.integrity_status === "CONTRADICTION" && verification?.contradictions?.length > 0
      ? "registries"
      : "forensics"
  );

  // Handle requirement selection -> locate physical evidence or show clean missing-evidence view
  const handleSelectClause = (clauseId: string) => {
    setSelectedClauseId(clauseId);
    setSelectedBlockId(null);

    if (!verification) {
      setActiveEvidence(null);
      return;
    }

    // Enforce EXACT requirement match
    const item = verification.verification_results.find(
      (r) => r.requirement_id === clauseId
    );

    // 1. If bidder submitted physical evidence for this requirement:
    if (item && item.evidence && item.evidence.length > 0 && item.evidence[0]) {
      const ev = item.evidence[0];
      const snippet = ev.snippet || (ev as any).raw_text_snippet || (ev as any).text || "";
      setActiveEvidence({
        document: ev.document || `${verification.bid_id}.pdf`,
        page: ev.page || 1,
        bbox: ev.bbox,
        snippet: snippet,
        requirement_id: item.requirement_id,
        expected: item.expected,
        actual: item.actual,
        operator_used: item.operator_used,
        status: item.status,
        reason: item.reason,
        grounding_state: "VERIFIED",
        confidence_heuristic: "HIGH",
      });
      return;
    }

    // 1b. If evidence array was empty but fact exists in dossier
    if (item?.fact_id && loadedDossier?.bidder?.facts && Array.isArray(loadedDossier.bidder.facts)) {
      const matchedFact = loadedDossier.bidder.facts.find((f: any) => f.fact_id === item.fact_id);
      if (matchedFact) {
        const factSnippet = matchedFact.raw_text_snippet || matchedFact.snippet || String(matchedFact.value || "");
        setActiveEvidence({
          document: matchedFact.source_document || `${verification.bid_id}.pdf`,
          page: matchedFact.page || 1,
          bbox: matchedFact.bbox,
          snippet: factSnippet,
          requirement_id: item.requirement_id,
          expected: item.expected,
          actual: item.actual,
          operator_used: item.operator_used,
          status: item.status,
          reason: item.reason,
          grounding_state: "VERIFIED",
          confidence_heuristic: "HIGH",
        });
        return;
      }
    }

    // 2. If bidder evidence is missing, check for tender-side requirement specification
    const tenderReq = loadedDossier?.tender?.requirements?.find(
      (tr: any) => tr.requirement_id === clauseId
    );
    if (tenderReq && tenderReq.evidence && tenderReq.evidence.length > 0 && tenderReq.evidence[0]) {
      const trEv = tenderReq.evidence[0];
      const trSnippet = trEv.snippet || (trEv as any).raw_text_snippet || tenderReq.description || "";
      setActiveEvidence({
        document: trEv.document || `${verification.tender_id}.pdf`,
        page: trEv.page || tenderReq.source_page || 1,
        bbox: trEv.bbox,
        snippet: trSnippet,
        requirement_id: item ? item.requirement_id : clauseId,
        expected: item?.expected ?? tenderReq.expected_value,
        actual: "MISSING (No bidder evidence submitted)",
        operator_used: item?.operator_used ?? tenderReq.operator,
        status: "MISSING",
        reason: item?.reason || `No physical evidence provided in bid submission for requirement ${clauseId}.`,
        grounding_state: "VERIFIED",
        confidence_heuristic: "HIGH",
      });
      return;
    }

    // 3. Clean missing-evidence state: Never leave previous requirement's evidence active!
    setActiveEvidence({
      document: `${verification.bid_id}.pdf`,
      page: 1,
      bbox: undefined,
      snippet: `No physical evidence submitted by bidder for requirement ${clauseId}. Evaluation verdict: ${item?.status || "MISSING"}. Deterministic reason: ${item?.reason || "Clause reference was not substantiated with a physical excerpt or document pointer in the submission."}`,
      requirement_id: item ? item.requirement_id : clauseId,
      expected: item?.expected ?? "—",
      actual: item?.actual ?? "MISSING",
      operator_used: item?.operator_used ?? "—",
      status: item?.status || "MISSING",
      reason: item?.reason || "No evidence submitted.",
      grounding_state: "UNVERIFIED",
      confidence_heuristic: "LOW",
    });
  };

  // Sync initial evidence when verification or dossier is loaded
  useEffect(() => {
    if (verification?.verification_results && verification.verification_results.length > 0) {
      const firstBidder = verification.verification_results.find(
        (r) => r.status !== "N/A" && r.status !== "N_A"
      );
      const target = firstBidder || verification.verification_results[0];
      handleSelectClause(target.requirement_id);
    } else {
      setSelectedClauseId(null);
      setSelectedBlockId(null);
      setActiveEvidence(null);
    }
  }, [verification, loadedDossier]);

  const handleSelectEvidenceBlock = (blockId: string) => {
    const block = physicalBlocks.find((b) => b.id === blockId);
    if (!block) return;

    setSelectedBlockId(blockId);
    setSelectedClauseId(null);
    setActiveEvidence({
      document: block.id === "BLK-001-02" ? "financial_annexure.pdf" : "technical_bid.pdf",
      page: block.page,
      block_id: block.id,
      bbox: block.bbox,
      snippet: block.text,
      grounding_state: block.grounding_state,
      confidence_heuristic: block.confidence_heuristic,
    });
    setActiveWorkspaceTab("forensics");
  };

  const handleSelectContradictionEvidence = (
    evidence: Record<string, any>,
    side: "A" | "B"
  ) => {
    const matchingBlock = physicalBlocks.find((block) =>
      block.text.includes(evidence.snippet.replace("...", "")) ||
      evidence.snippet.includes(block.text.split("\n").pop() || "__no_match__")
    );

    if (matchingBlock) {
      handleSelectEvidenceBlock(matchingBlock.id);
      return;
    }

    setSelectedClauseId(null);
    setSelectedBlockId(null);
    setActiveEvidence({
      document: evidence.document,
      page: evidence.page,
      snippet: evidence.snippet,
      grounding_state: "VERIFIED",
      confidence_heuristic: "HIGH",
      requirement_id: `CONTRA-000001 · EVIDENCE ${side}`,
    });
    setActiveWorkspaceTab("forensics");
  };

  const handleTriggerEvidence = (item: VerificationResult, pos?: { x: number; y: number }) => {
    handleSelectClause(item.requirement_id);
    if (pos) {
      setInspectorPos(pos);
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-[calc(100vh-6rem)] items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          <p className="text-sm font-semibold text-slate-700">Loading verification dossier...</p>
        </div>
      </div>
    );
  }

  if (loadError || !verification) {
    return (
      <div className="flex h-[calc(100vh-6rem)] items-center justify-center">
        <div className="max-w-md rounded-xl border border-rose-200 bg-white p-6 text-center shadow-sm">
          <AlertTriangle className="mx-auto h-8 w-8 text-rose-600" />
          <h2 className="mt-3 text-base font-bold text-slate-900">Verification Dossier Unavailable</h2>
          <p className="mt-1 text-xs text-slate-500">{loadError || `Verification '${id}' not found.`}</p>
          <Link
            to="/verify/new"
            className="mt-4 inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-xs font-bold text-white hover:bg-slate-800"
          >
            <ArrowLeft className="h-4 w-4" /> Return to Intake
          </Link>
        </div>
      </div>
    );
  }

  const isProcessCondition = (r: VerificationResult) => {
    const s = (r.status || "").toUpperCase();
    const rt = (r.requirement_type || "").toUpperCase();
    const ps = (r.precedence_chain?.status || "").toUpperCase();
    return (
      s === "N/A" ||
      s === "N_A" ||
      rt === "PROCESS_CONDITION" ||
      rt === "INFORMATIONAL" ||
      rt === "GENERAL_POLICY" ||
      ps === "PROCESS_CONDITION" ||
      ps === "INFORMATIONAL" ||
      ps === "GENERAL_POLICY"
    );
  };

  const bidderResults = verification.verification_results.filter((r) => !isProcessCondition(r));
  const processResults = verification.verification_results.filter((r) => isProcessCondition(r));

  const passCount = bidderResults.filter((r) => r.status === "PASS").length;
  const failCount = bidderResults.filter((r) => r.status === "FAIL").length;
  const reviewCount = bidderResults.filter((r) => r.status === "REVIEW" || r.status === "PARTIAL").length;
  const missingCount = bidderResults.filter((r) => r.status === "MISSING").length;
  const officerQueueCount = verification.human_review_items.length;

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)] space-y-2.5 font-sans select-none">
      {/* 1. GLOBAL FORENSIC COMMAND BAR */}
      <div className="bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 shadow-md flex flex-wrap items-center justify-between gap-3 text-white shrink-0">
        <div className="flex items-center gap-3">
          <Link
            to="/dashboard"
            className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-white transition-colors"
            title="Back to Dashboard"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>

          <div className="border-l border-slate-800 pl-3">
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold tracking-tight text-white">
                {companyName}
              </h1>
              <span className="font-mono text-[11px] font-bold px-2 py-0.2 rounded bg-slate-800 text-blue-400 border border-slate-700">
                {verification.bid_id}
              </span>
            </div>
            <div className="flex items-center gap-2.5 text-[10px] font-mono text-slate-400 mt-0.5">
              <span>Tender: {verification.tender_id}</span>
              <span>•</span>
              <span>Run ID: {verification.deterministic_run_id}</span>
              <span>•</span>
              <span>{verification.generated_at}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-900 px-2.5 py-1 rounded border border-slate-800">
            <span className="text-[10px] font-mono text-slate-400 uppercase">Compliance:</span>
            <ComplianceBadge status={verification.compliance_status} size="sm" />
          </div>

          <div className="flex items-center gap-2 bg-slate-900 px-2.5 py-1 rounded border border-slate-800">
            <span className="text-[10px] font-mono text-slate-400 uppercase">Integrity:</span>
            <IntegrityBadge status={verification.integrity_status} size="sm" />
          </div>

          <OverallBadge status={verification.overall_status} size="md" />
        </div>
      </div>

      {/* 2. ANALYTICAL SUMMARY RAIL */}
      <div className="bg-white border border-slate-200 rounded-lg px-4 py-1.5 flex items-center justify-between text-xs shrink-0 shadow-2xs">
        <div className="flex items-center gap-4 font-mono text-[11px]">
          <div>
            <span className="text-slate-400 mr-1">OBLIGATIONS:</span>
            <span className="font-bold text-slate-800">
              {bidderResults.length}
            </span>
          </div>

          <div>
            <span className="text-emerald-600 mr-1 font-bold">● PASS:</span>
            <span className="font-bold text-emerald-800">{passCount}</span>
          </div>

          <div>
            <span className="text-rose-600 mr-1 font-bold">▲ FAILED:</span>
            <span className="font-bold text-rose-800">{failCount}</span>
          </div>

          <div>
            <span className="text-slate-500 mr-1">○ MISSING:</span>
            <span className="font-bold text-slate-600">{missingCount}</span>
          </div>

          <div className="border-l border-slate-200 pl-4">
            <span className="text-amber-600 mr-1 font-bold">◆ REVIEW:</span>
            <span className="font-bold text-amber-800">{reviewCount}</span>
          </div>

          <div className="border-l border-slate-200 pl-4">
            <span className="text-purple-600 mr-1 font-bold">📋 QUEUE:</span>
            <span className="font-bold text-purple-800">{officerQueueCount}</span>
          </div>

          <div className="border-l border-slate-200 pl-4">
            <span className="text-slate-400 mr-1">PROCESS COND:</span>
            <span className="font-bold text-slate-600">{processResults.length}</span>
          </div>
        </div>

        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={() => setActiveWorkspaceTab("forensics")}
            className={`px-3 py-1 rounded text-xs font-semibold transition-colors ${
              activeWorkspaceTab === "forensics"
                ? "bg-slate-900 text-white shadow-2xs"
                : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            Document & Matrix
          </button>
          <button
            type="button"
            onClick={() => setActiveWorkspaceTab("registries")}
            className={`px-3 py-1 rounded text-xs font-semibold transition-colors ${
              activeWorkspaceTab === "registries"
                ? "bg-slate-900 text-white shadow-2xs"
                : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            Registries & Contradictions ({verification.contradictions.length})
          </button>
          <button
            type="button"
            onClick={() => setActiveWorkspaceTab("dossier")}
            className={`px-3 py-1 rounded text-xs font-semibold transition-colors ${
              activeWorkspaceTab === "dossier"
                ? "bg-slate-900 text-white shadow-2xs"
                : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            Dossier JSON
          </button>
        </div>
      </div>

      {/* 3. MAIN WORKSPACE CONTENT */}
      {activeWorkspaceTab === "forensics" && (
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-2.5 min-h-0">
          {/* Left Pane: Document Canvas (45%) */}
          <div className="lg:col-span-5 h-full min-h-0">
            <DocumentCanvas
              documentName={activeEvidence?.document || `${verification.bid_id}.pdf`}
              bidId={verification.bid_id}
              textBlocks={physicalBlocks}
              selectedClauseId={selectedClauseId}
              selectedBlockId={selectedBlockId}
              activePage={activeEvidence?.page}
              onSelectClause={handleSelectClause}
              onSelectBlock={handleSelectEvidenceBlock}
              onHoverEvidence={(ev, pos) => {
                setHoveredEvidence(ev);
                setInspectorPos(pos || null);
              }}
            />
          </div>

          {/* Right Pane: Split Matrix (Top) + Docked Evidence Inspector (Bottom) */}
          <div className="lg:col-span-7 flex flex-col h-full min-h-0 space-y-2">
            {/* Top: TanStack Matrix Table */}
            <div className="flex-1 min-h-0">
              <RequirementMatrixTable
                data={verification.verification_results}
                selectedClauseId={selectedClauseId}
                onSelectClause={handleSelectClause}
                onTriggerEvidence={handleTriggerEvidence}
              />
            </div>

            {/* Bottom: Docked Forensic Evidence Inspector */}
            {activeEvidence && (
              <div className="h-44 bg-slate-950 border border-slate-800 rounded-lg p-3 text-slate-100 shadow-md flex flex-col justify-between shrink-0 font-sans">
                {/* Header */}
                <div className="flex items-center justify-between pb-1.5 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <FileText className="w-3.5 h-3.5 text-blue-400" />
                    <span className="font-mono text-xs font-bold text-slate-200">
                      {activeEvidence.document} · Page {activeEvidence.page}
                    </span>
                    <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-blue-950 text-blue-300 border border-blue-800">
                      BBox: [{activeEvidence.bbox && activeEvidence.bbox.some((c) => c > 0) ? activeEvidence.bbox.map((n) => Math.round(n)).join(", ") : "None / Unspecified"}]
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    {activeEvidence.status === "MISSING" ? (
                      <span className="inline-flex items-center gap-1 px-1.5 py-0.2 rounded text-[10px] font-mono font-bold bg-rose-950 text-rose-300 border border-rose-800">
                        <AlertTriangle className="w-3 h-3 text-rose-400" />
                        NO BIDDER EVIDENCE SUBMITTED
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-1.5 py-0.2 rounded text-[10px] font-mono font-bold bg-emerald-950 text-emerald-300 border border-emerald-800">
                        <ShieldCheck className="w-3 h-3 text-emerald-400" />
                        PHYSICAL EVIDENCE GROUNDED
                      </span>
                    )}
                    <span className="font-mono text-[11px] font-bold text-amber-400">
                      {activeEvidence.requirement_id}
                    </span>
                  </div>
                </div>

                {/* Verbatim Snippet */}
                <div className={`my-1.5 p-2 rounded font-mono text-[11px] leading-relaxed overflow-y-auto max-h-16 ${
                  activeEvidence.status === "MISSING"
                    ? "bg-rose-950/30 border border-rose-900/60 text-rose-200"
                    : "bg-slate-900 border border-slate-800/90 text-slate-200"
                }`}>
                  {activeEvidence.status === "MISSING" ? (
                    <span className="italic text-rose-300">{activeEvidence.snippet}</span>
                  ) : (
                    <>“{activeEvidence.snippet}”</>
                  )}
                </div>

                {/* Traceability Bar */}
                <div className="pt-1.5 border-t border-slate-800 flex items-center justify-between text-[10px] font-mono text-slate-400">
                  <div className="flex items-center gap-3">
                    <span>Threshold: <strong className="text-slate-200">{String(activeEvidence.expected ?? "—")}</strong></span>
                    <span>•</span>
                    <span>Extracted: <strong className={activeEvidence.status === "MISSING" ? "text-rose-400" : "text-blue-300"}>{activeEvidence.actual ?? "—"}</strong></span>
                    <span>•</span>
                    <span>Verdict: <strong className={activeEvidence.status === "PASS" ? "text-emerald-400" : activeEvidence.status === "FAIL" || activeEvidence.status === "MISSING" ? "text-rose-400" : "text-amber-400"}>{activeEvidence.status ?? "EVIDENCE"}</strong></span>
                  </div>
                  <span className="text-slate-500">Step 4 Deterministic Rule Trace</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Secondary Workspace: Registries & Contradictions */}
      {activeWorkspaceTab === "registries" && (
        <div className="flex-1 bg-white border border-slate-200 rounded-lg p-6 overflow-y-auto space-y-6">
          <div>
            <h3 className="text-sm font-bold text-slate-900 pb-2 border-b border-slate-200 flex items-center justify-between">
              <span>Government Registry Verification (Step 5 Mock Adapters)</span>
              <span className="text-[11px] font-mono text-slate-500">GOVERNMENT VERIFICATION FABRIC</span>
            </h3>

                      {verification.government_checks.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              {verification.government_checks.map((g, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-lg border border-slate-200 bg-slate-50/70 space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900 text-xs">
                      {g.adapter_name}
                    </span>

                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                      {g.status}
                    </span>
                  </div>

                  <div className="font-mono text-xs text-slate-600">
                    ID: {g.queried_identifier}
                  </div>

                  <p className="text-[11px] text-slate-500">
                    {g.reason}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="mt-3">
              <div className="flex items-center gap-3 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3">
                <div className="w-8 h-8 rounded-full bg-white border border-slate-200 flex items-center justify-center shrink-0">
                  <ShieldCheck className="w-4 h-4 text-slate-400" />
                </div>

                <div>
                  <p className="text-xs font-semibold text-slate-700">
                    No registry checks required
                  </p>

                  <p className="text-[11px] text-slate-500 mt-0.5">
                    No government registry adapter was invoked for this finding.
                  </p>
                </div>
              </div>
            </div>
          )}
          </div>

          <div>
            <h3 className="text-sm font-bold text-slate-900 pb-2 border-b border-slate-200 flex items-center justify-between">
              <span>Cross-Document Integrity Findings</span>
              <IntegrityBadge status={verification.integrity_status} size="sm" />
            </h3>

            {verification.contradictions.length === 0 ? (
              <div className="p-8 text-center text-slate-500 bg-slate-50 rounded-lg mt-4 border border-dashed border-slate-200">
                <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
                <p className="text-xs font-semibold text-slate-800">Zero Inconsistencies Detected</p>
                <p className="text-[11px] text-slate-500 mt-1">
                  All entity identifiers, turnover figures, and declarations match bitwise across submitted documents.
                </p>
              </div>
            ) : (
              <div className="space-y-3 mt-4">
                {verification.contradictions.map((c) => (
                                  <div
                  key={c.finding_id}
                  className="p-4 bg-rose-50 border border-rose-200 rounded-lg space-y-3"
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className="font-mono font-bold text-rose-900 text-xs">
                      {c.finding_id}
                    </span>

                    <span className="px-2 py-1 rounded text-[10px] font-bold bg-rose-200 text-rose-900">
                      {c.severity} SEVERITY
                    </span>
                  </div>

                  <div>
                    <h4 className="text-base font-bold text-slate-900">
                      GSTIN discrepancy detected
                    </h4>

                    <p className="mt-1 text-xs text-slate-600">
                      {c.description}
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] gap-3 items-stretch">

                    {/* Evidence A */}
                    <div className="bg-white border border-rose-200 rounded-lg p-3">
                      <div className="flex items-center justify-between gap-2 mb-2">
                        <div>
                          <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                            Technical Schedule
                          </p>

                          <p className="text-[10px] text-slate-400">
                            Page {c.evidence_a.page}
                          </p>
                        </div>

                        <span className="text-[10px] font-mono font-semibold text-slate-400">
                          EVIDENCE A
                        </span>
                      </div>

                      <div className="rounded-md bg-slate-50 border border-slate-200 p-3">
                        <p className="font-mono text-sm font-bold text-slate-900 break-all">
                          {c.evidence_a.snippet}
                        </p>
                      </div>

                      <button
                        type="button"
                        onClick={() =>
                          handleSelectContradictionEvidence(
                            c.evidence_a,
                            "A"
                          )
                        }
                        className="mt-3 w-full flex items-center justify-center gap-2 px-3 py-2 rounded-md border border-rose-200 bg-white text-xs font-semibold text-rose-700 hover:bg-rose-50 transition-colors"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        View in document
                      </button>
                    </div>

                    {/* Mismatch indicator */}
                    <div className="flex md:flex-col items-center justify-center gap-2 py-1">
                      <div className="hidden md:block h-full w-px bg-rose-200" />

                      <div className="w-10 h-10 shrink-0 rounded-full bg-rose-100 border border-rose-300 flex items-center justify-center">
                        <span className="text-lg font-bold text-rose-600">
                          ≠
                        </span>
                      </div>

                      <div className="hidden md:block h-full w-px bg-rose-200" />
                    </div>

                    {/* Evidence B */}
                    <div className="bg-white border border-rose-200 rounded-lg p-3">
                      <div className="flex items-center justify-between gap-2 mb-2">
                        <div>
                          <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                            Financial Annexure
                          </p>

                          <p className="text-[10px] text-slate-400">
                            Page {c.evidence_b.page}
                          </p>
                        </div>

                        <span className="text-[10px] font-mono font-semibold text-slate-400">
                          EVIDENCE B
                        </span>
                      </div>

                      <div className="rounded-md bg-slate-50 border border-slate-200 p-3">
                        <p className="font-mono text-sm font-bold text-slate-900 break-all">
                          {c.evidence_b.snippet}
                        </p>
                      </div>

                      <button
                        type="button"
                        onClick={() =>
                          handleSelectContradictionEvidence(
                            c.evidence_b,
                            "B"
                          )
                        }
                        className="mt-3 w-full flex items-center justify-center gap-2 px-3 py-2 rounded-md border border-rose-200 bg-white text-xs font-semibold text-rose-700 hover:bg-rose-50 transition-colors"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        View in document
                      </button>
                    </div>
                  </div>

                  <div className="flex items-center justify-center gap-2 py-2 px-3 rounded-md bg-rose-100 border border-rose-200">
                    <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />

                    <span className="text-[11px] font-bold uppercase tracking-wider text-rose-800">
                      Values do not match
                    </span>
                  </div>

                  {c.hint && (
                    <p className="text-[11px] text-slate-500 border-t border-rose-100 pt-2">
                      <span className="font-semibold text-slate-700">
                        Review note:
                      </span>{" "}
                      {c.hint}
                    </p>
                  )}
                </div>
                

                ))}
                              <div className="mt-4 rounded-lg border border-amber-200 bg-amber-50/60 p-4">
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-amber-700">
                        Recommended Action
                      </span>

                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800">
                        HUMAN REVIEW
                      </span>
                    </div>

                    <h4 className="text-sm font-bold text-slate-900">
                      Hold for adjudication
                    </h4>

                    <p className="mt-1 text-xs text-slate-600 max-w-2xl">
                      GSTIN inconsistency requires officer verification before
                      the bid can proceed.
                    </p>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-2 shrink-0">
                    <button
                      type="button"
                      onClick={() => navigate("/review")}
                      className="inline-flex items-center justify-center gap-2 px-3 py-2 rounded-md bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800 transition-colors"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      Route to Review
                    </button>

                    <button
                      type="button"
                      onClick={() => setActiveWorkspaceTab("dossier")}
                      className="inline-flex items-center justify-center gap-2 px-3 py-2 rounded-md border border-slate-300 bg-white text-slate-700 text-xs font-semibold hover:bg-slate-50 transition-colors"
                    >
                      <FileText className="w-3.5 h-3.5" />
                      Open Dossier
                    </button>
                  </div>
                </div>

                <div className="mt-3 pt-3 border-t border-amber-200">
                  <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-2">
                    Evidence Basis
                  </p>

                  <div className="flex flex-wrap gap-2">
                    <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded bg-white border border-slate-200 text-[10px] font-medium text-slate-600">
                      <FileText className="w-3 h-3 text-slate-400" />
                      Technical Schedule · Page 1
                    </span>

                    <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded bg-white border border-slate-200 text-[10px] font-medium text-slate-600">
                      <FileText className="w-3 h-3 text-slate-400" />
                      Financial Annexure · Page 2
                    </span>

                    <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded bg-white border border-slate-200 text-[10px] font-medium text-slate-600">
                      <AlertTriangle className="w-3 h-3 text-rose-500" />
                      HIGH severity contradiction
                    </span>
                  </div>
                </div>
              </div>
              </div>
              
            )}
          </div>
        </div>
      )}

      {/* Third Workspace: Audit Dossier JSON */}
      {activeWorkspaceTab === "dossier" && (
        <div className="flex-1 bg-white border border-slate-200 rounded-lg p-5 overflow-hidden flex flex-col">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200 shrink-0">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Machine-Readable Audit Dossier</h3>
              <p className="text-xs text-slate-500 font-mono">
                Run ID: {verification.deterministic_run_id || (loadedDossier as any)?.audit_metadata?.deterministic_run_id || "RUN-LIVE"}
              </p>
            </div>
            <button
              type="button"
              onClick={() => {
                const blob = new Blob([JSON.stringify(loadedDossier || verification, null, 2)], { type: "application/json" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `dossier-${verification.verification_id}.json`;
                a.click();
              }}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download JSON Dossier</span>
            </button>
          </div>
          <pre className="flex-1 p-4 bg-slate-950 text-slate-200 rounded-lg font-mono text-[11px] overflow-auto mt-3">
            {JSON.stringify(loadedDossier || verification, null, 2)}
          </pre>
        </div>
      )}

      {/* Floating Tooltip Inspector (active on hover over document canvas blocks) */}
      <EvidenceInspector
        evidence={hoveredEvidence}
        position={inspectorPos}
        onClose={() => setHoveredEvidence(null)}
        isPinned={false}
      />
    </div>
  );
};