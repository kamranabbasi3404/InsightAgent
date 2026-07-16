"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import ChatWindow from "./components/ChatWindow";
import ReasoningTrace from "./components/ReasoningTrace";
import UploadPanel from "./components/UploadPanel";
import {
  checkHealth,
  getDocuments,
  streamChat,
} from "@/lib/api";
import type { DocumentInfo, TraceStep, Citation, Conflict } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  conflicts?: Conflict[];
  route?: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState("");
  const [traceSteps, setTraceSteps] = useState<TraceStep[]>([]);
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");
  const [error, setError] = useState<string | null>(null);

  const hasLoaded = useRef(false);

  // Load chat history from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem("insight_agent_chat_history");
    if (saved) {
      try {
        setMessages(JSON.parse(saved));
      } catch (e) {
        console.error("Failed to parse chat history:", e);
      }
    }
    hasLoaded.current = true;
  }, []);

  // Save chat history to localStorage when messages update
  useEffect(() => {
    if (hasLoaded.current) {
      localStorage.setItem("insight_agent_chat_history", JSON.stringify(messages));
    }
  }, [messages]);

  // Check backend health on mount
  useEffect(() => {
    checkHealth()
      .then(() => setBackendStatus("online"))
      .catch(() => setBackendStatus("offline"));
  }, []);


  // Load documents on mount and after changes
  const refreshDocuments = useCallback(async () => {
    try {
      const res = await getDocuments();
      setDocuments(res.documents);
    } catch {
      // Silently fail — documents list is non-critical
    }
  }, []);

  useEffect(() => {
    if (backendStatus === "online") {
      refreshDocuments();
    }
  }, [backendStatus, refreshDocuments]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const query = input.trim();
    if (!query || isProcessing) return;

    setInput("");
    setError(null);
    setTraceSteps([]);
    setIsProcessing(true);
    setProcessingStep("Analyzing query...");

    // Add user message
    setMessages((prev) => [...prev, { role: "user", content: query }]);

    try {
      let finalAnswer = "";
      let finalCitations: Citation[] = [];
      let finalConflicts: Conflict[] = [];
      let finalRoute = "";

      for await (const event of streamChat(query)) {
        switch (event.type) {
          case "trace": {
            const traceData = event.data as TraceStep;
            setTraceSteps((prev) => [...prev, traceData]);
            setProcessingStep(`${traceData.icon} ${traceData.label}...`);
            break;
          }
          case "answer": {
            const answerData = event.data as {
              answer: string;
              citations: Citation[];
              conflicts: Conflict[];
              route: string;
            };
            finalAnswer = answerData.answer;
            finalCitations = answerData.citations;
            finalConflicts = answerData.conflicts;
            finalRoute = answerData.route;
            break;
          }
          case "error": {
            const errorData = event.data as { error: string };
            setError(errorData.error);
            break;
          }
          case "done":
            break;
        }
      }

      if (finalAnswer) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: finalAnswer,
            citations: finalCitations,
            conflicts: finalConflicts,
            route: finalRoute,
          },
        ]);
      } else if (!error) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "I wasn't able to generate a response. Please try again.",
          },
        ]);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "An error occurred";
      setError(message);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `⚠ Error: ${message}. Please check that the backend is running and your API keys are configured.`,
        },
      ]);
    } finally {
      setIsProcessing(false);
      setProcessingStep("");
    }
  };

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <header className="flex items-center justify-between px-5 py-3 border-b border-border bg-bg-card/80 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
            <span className="text-lg">🔬</span>
          </div>
          <div>
            <h1 className="text-base font-bold text-text tracking-tight">InsightAgent</h1>
            <p className="text-[10px] text-text-muted">Agentic Research Assistant</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Backend status */}
          <div className="flex items-center gap-1.5">
            <span
              className={`w-2 h-2 rounded-full ${
                backendStatus === "online"
                  ? "bg-green-500"
                  : backendStatus === "offline"
                  ? "bg-conflict"
                  : "bg-amber animate-pulse"
              }`}
            />
            <span className="text-[10px] text-text-muted capitalize">{backendStatus}</span>
          </div>

          {/* Clear Chat */}
          {messages.length > 0 && (
            <button
              onClick={() => {
                if (confirm("Are you sure you want to clear the chat history?")) {
                  setMessages([]);
                  localStorage.removeItem("insight_agent_chat_history");
                }
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border text-xs text-text-secondary hover:text-conflict hover:border-conflict hover:bg-conflict-light/10 transition-all cursor-pointer"
            >
              <span>🗑</span>
              <span>Clear Chat</span>
            </button>
          )}

          {/* Document count */}
          <button
            onClick={() => setIsUploadOpen(true)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border
              hover:border-primary hover:bg-primary/5 transition-all text-sm"
          >
            <span className="text-xs">📁</span>
            <span className="text-xs font-medium text-text">
              {documents.length > 0 ? `${documents.length} Doc${documents.length !== 1 ? "s" : ""}` : "Upload"}
            </span>
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Chat Area */}
        <div className="flex-1 flex flex-col min-w-0">
          <ChatWindow
            messages={messages}
            isProcessing={isProcessing}
            processingStep={processingStep}
          />

          {/* Error banner */}
          {error && (
            <div className="mx-4 mb-2 p-3 rounded-lg bg-conflict-light border border-conflict/20 text-conflict text-xs flex items-center gap-2">
              <span>⚠</span>
              <span>{error}</span>
              <button
                onClick={() => setError(null)}
                className="ml-auto text-conflict/60 hover:text-conflict"
              >
                ✕
              </button>
            </div>
          )}

          {/* Input Area */}
          <div className="px-4 py-3 border-t border-border bg-bg-card/50">
            <form onSubmit={handleSubmit} className="flex items-center gap-2 max-w-3xl mx-auto">
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={
                    backendStatus === "offline"
                      ? "Backend is offline — start the server first"
                      : "Ask a research question..."
                  }
                  disabled={isProcessing || backendStatus === "offline"}
                  className="w-full px-4 py-2.5 rounded-xl border border-border bg-bg-input text-sm text-text
                    placeholder:text-text-muted focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20
                    disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                />
              </div>
              <button
                type="submit"
                disabled={!input.trim() || isProcessing || backendStatus === "offline"}
                className="px-4 py-2.5 rounded-xl bg-primary text-white text-sm font-medium
                  hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-primary/30
                  disabled:opacity-40 disabled:cursor-not-allowed transition-all
                  flex items-center gap-1.5"
              >
                {isProcessing ? (
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <span>→</span>
                )}
                Send
              </button>
            </form>
          </div>
        </div>

        {/* Reasoning Trace Panel — defaults to open on desktop per design.md */}
        <ReasoningTrace steps={traceSteps} isProcessing={isProcessing} />
      </div>

      {/* Upload Modal */}
      <UploadPanel
        documents={documents}
        onDocumentsChange={refreshDocuments}
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
      />
    </div>
  );
}
