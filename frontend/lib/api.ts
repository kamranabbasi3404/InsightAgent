/**
 * API Client — Centralized API calls to the InsightAgent backend.
 * Components should not construct fetch calls inline (per rules.md).
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// --- Types ---

export interface UploadResponse {
  filename: string;
  pages_extracted: number;
  chunks_created: number;
  message: string;
}

export interface DocumentInfo {
  filename: string;
  chunk_count: number;
}

export interface DocumentsResponse {
  documents: DocumentInfo[];
  total: number;
}

export interface Citation {
  id: number;
  type: "pdf" | "web";
  source: string;
  page?: number;
  title?: string;
  snippet: string;
}

export interface Conflict {
  topic: string;
  local_claim: string;
  web_claim: string;
  explanation: string;
}

export interface TraceStep {
  step: string;
  icon: string;
  label: string;
  summary: string;
  detail: string;
  sub_queries?: string[];
  result_count?: number;
  conflicts?: Conflict[];
  is_retry?: boolean;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  trace: TraceStep[];
  conflicts: Conflict[];
  route: string;
}

export interface HealthResponse {
  status: string;
  service: string;
}

// --- API Functions ---

export async function checkHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_URL}/health`);
  if (!res.ok) throw new Error("Backend health check failed");
  return res.json();
}

export async function uploadPDF(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(error.detail || "Upload failed");
  }

  return res.json();
}

export async function getDocuments(): Promise<DocumentsResponse> {
  const res = await fetch(`${API_URL}/api/documents`);
  if (!res.ok) throw new Error("Failed to fetch documents");
  return res.json();
}

export async function deleteDocument(filename: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/documents/${encodeURIComponent(filename)}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete document");
}

export async function sendChat(query: string): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Chat request failed" }));
    throw new Error(error.detail || "Chat request failed");
  }

  return res.json();
}

/**
 * Stream chat via SSE — yields trace events and final answer as they arrive.
 */
export async function* streamChat(
  query: string
): AsyncGenerator<{ type: "trace" | "answer" | "done" | "error"; data: unknown }> {
  const res = await fetch(`${API_URL}/api/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Stream failed" }));
    throw new Error(error.detail || "Stream failed");
  }

  const reader = res.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // Parse SSE events from buffer
    const events = buffer.split("\n\n");
    buffer = events.pop() || ""; // Keep incomplete event in buffer

    for (const event of events) {
      if (!event.trim()) continue;

      const lines = event.split("\n");
      let eventType = "";
      let eventData = "";

      for (const line of lines) {
        if (line.startsWith("event: ")) {
          eventType = line.slice(7).trim();
        } else if (line.startsWith("data: ")) {
          eventData = line.slice(6);
        }
      }

      if (eventType && eventData) {
        try {
          const parsed = JSON.parse(eventData);
          yield { type: eventType as "trace" | "answer" | "done" | "error", data: parsed };
        } catch {
          // Skip malformed events
        }
      }
    }
  }
}
