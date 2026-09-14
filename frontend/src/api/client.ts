// Typed API Client Foundation for GeM Procurement Verification Engine

import {
  HealthResponse,
  AggregatedVerification,
  VerificationDossier,
  HumanReviewItem,
} from "../types";

export class ApiError extends Error {
  public status: number;
  public detail?: string | null;

  constructor(status: number, message: string, detail?: string | null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        Accept: "application/json",
        ...(options.headers || {}),
      },
    });

    if (!response.ok) {
      let errorMsg = `HTTP Error ${response.status}: ${response.statusText}`;
      let detail: string | null = null;
      try {
        const errorJson = await response.json();
        if (errorJson && (errorJson.error || errorJson.detail)) {
          errorMsg = errorJson.error || errorJson.detail;
          detail = errorJson.detail || null;
        }
      } catch {
        // Fallback to text status
      }
      throw new ApiError(response.status, errorMsg, detail);
    }

    return (await response.json()) as T;
  } catch (err: any) {
    if (err instanceof ApiError) {
      throw err;
    }
    throw new ApiError(0, err.message || "Failed to communicate with verification backend.");
  }
}

export const apiClient = {
  /**
   * Health Check
   */
  async getHealth(): Promise<HealthResponse> {
    return request<HealthResponse>("/health");
  },

  /**
   * Retrieves full aggregated verification by ID
   */
  async getVerification(verificationId: string): Promise<AggregatedVerification> {
    return request<AggregatedVerification>(`/api/v1/verification/${encodeURIComponent(verificationId)}`);
  },

  /**
   * Retrieves complete machine-readable verification dossier by ID
   */
  async getDossier(verificationId: string): Promise<VerificationDossier> {
    return request<VerificationDossier>(`/api/v1/verification/${encodeURIComponent(verificationId)}/dossier`);
  },

  /**
   * Retrieves human review queue items for a verification
   */
  async getReviewItems(verificationId: string): Promise<HumanReviewItem[]> {
    return request<HumanReviewItem[]>(`/api/v1/verification/${encodeURIComponent(verificationId)}/review-items`);
  },

  /**
   * Retrieves all persisted verifications across backend disk cache and session
   */
  async getVerifications(): Promise<AggregatedVerification[]> {
    return request<AggregatedVerification[]>("/api/v1/verifications");
  },

  /**
   * Retrieves all human review queue items across all persisted verifications
   */
  async getReviewQueue(): Promise<HumanReviewItem[]> {
    return request<HumanReviewItem[]>("/api/v1/review-queue");
  },

  /**
   * Executes verification on uploaded tender & bid documents
   */
  async verifyBid(formData: FormData): Promise<AggregatedVerification> {
    return request<AggregatedVerification>("/api/v1/verify", {
      method: "POST",
      body: formData,
    });
  },

  /**
   * Executes streamed verification on uploaded tender & bid documents,
   * yielding real-time backend stage progression events.
   */
  async verifyBidStream(
    formData: FormData,
    onProgress: (event: StageProgressEvent) => void,
    signal?: AbortSignal
  ): Promise<AggregatedVerification> {
    const url = `${BASE_URL}/api/v1/verify-stream`;
    const response = await fetch(url, {
      method: "POST",
      body: formData,
      signal,
      headers: {
        Accept: "text/event-stream",
      },
    });

    if (!response.ok) {
      let errorMsg = `HTTP Error ${response.status}: ${response.statusText}`;
      let detail: string | null = null;
      try {
        const errorJson = await response.json();
        if (errorJson && (errorJson.error || errorJson.detail)) {
          errorMsg = errorJson.error || errorJson.detail;
          detail = errorJson.detail || null;
        }
      } catch {
        // Fallback to text
      }
      throw new ApiError(response.status, errorMsg, detail);
    }

    if (!response.body) {
      throw new ApiError(0, "Response stream body is unavailable.");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";
    let finalResult: AggregatedVerification | null = null;
    let failureError: string | null = null;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const normalized = buffer.replace(/\r\n/g, "\n");
      const chunks = normalized.split("\n\n");
      buffer = chunks.pop() || "";

      for (const chunk of chunks) {
        const lines = chunk.split("\n");
        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith("data:")) continue;
          const jsonStr = trimmed.slice(5).trim();
          if (!jsonStr) continue;

          try {
            const data = JSON.parse(jsonStr) as StreamVerificationEvent;
            if (data.event === "STAGE_PROGRESS") {
              onProgress(data);
            } else if (data.event === "VERIFICATION_COMPLETED") {
              finalResult = data.result;
            } else if (data.event === "VERIFICATION_FAILED") {
              failureError = data.error;
            }
          } catch (parseErr) {
            console.warn("Failed to parse SSE payload:", jsonStr, parseErr);
          }
        }
      }
    }

    if (failureError) {
      throw new ApiError(500, failureError);
    }

    if (!finalResult) {
      throw new ApiError(500, "Verification stream completed without receiving final verification result.");
    }

    return finalResult;
  },

  /**
   * Procurement Officer Adjudication / Override
   */
  async adjudicate(
    verificationId: string,
    payload: {
      target_id: string;
      decision: string;
      officer_id: string;
      officer_name: string;
      justification: string;
      officer_role?: string;
      reference_document?: string;
      target_type?: string;
    }
  ): Promise<any> {
    return request<any>(`/api/v1/verification/${encodeURIComponent(verificationId)}/adjudicate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  },

  /**
   * Retrieves complete audit trail and officer adjudication records
   */
  async getAuditTrail(verificationId: string): Promise<any> {
    return request<any>(`/api/v1/verification/${encodeURIComponent(verificationId)}/audit-trail`);
  },

  /**
   * Executes deterministic replay verification against stored snapshot
   */
  async replayVerification(verificationId: string): Promise<any> {
    return request<any>(`/api/v1/verification/${encodeURIComponent(verificationId)}/replay`, {
      method: "POST",
    });
  },
};

export interface StageProgressEvent {
  event: "STAGE_PROGRESS";
  step: number;
  status: "RUNNING" | "COMPLETED" | "FAILED";
  message: string;
  meta?: Record<string, any>;
}

export interface VerificationCompletedEvent {
  event: "VERIFICATION_COMPLETED";
  result: AggregatedVerification;
}

export interface VerificationFailedEvent {
  event: "VERIFICATION_FAILED";
  error: string;
}

export type StreamVerificationEvent =
  | StageProgressEvent
  | VerificationCompletedEvent
  | VerificationFailedEvent;

