"use client";

import { useRef, useEffect } from "react";
import CitationChip from "./CitationChip";
import type { Citation, Conflict } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  conflicts?: Conflict[];
  route?: string;
}

interface ChatWindowProps {
  messages: Message[];
  isProcessing: boolean;
  processingStep: string;
}

function RouteIndicator({ route }: { route: string }) {
  const routeConfig: Record<string, { icon: string; label: string; color: string }> = {
    local_only: { icon: "📄", label: "Local Documents", color: "text-primary" },
    web_only: { icon: "🌐", label: "Web Search", color: "text-amber" },
    hybrid: { icon: "🔀", label: "Hybrid (Local + Web)", color: "text-primary" },
    no_retrieval: { icon: "💬", label: "Direct Response", color: "text-text-secondary" },
  };

  const config = routeConfig[route] || routeConfig["no_retrieval"];

  return (
    <span className={`inline-flex items-center gap-1 text-[10px] font-medium ${config.color} bg-bg-sidebar rounded-full px-2 py-0.5`}>
      {config.icon} {config.label}
    </span>
  );
}

function ConflictBanner({ conflicts }: { conflicts: Conflict[] }) {
  if (!conflicts.length) return null;

  return (
    <div className="mt-3 space-y-2">
      {conflicts.map((conflict, i) => (
        <div
          key={i}
          className="p-3 rounded-lg border-l-3 border-conflict bg-conflict-light/40"
        >
          <div className="flex items-center gap-1.5 mb-1.5">
            <span className="text-conflict text-sm">⚠</span>
            <span className="text-xs font-semibold text-conflict">
              Conflict Detected: {conflict.topic}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-[11px]">
            <div className="p-2 rounded bg-bg-card border border-border-light">
              <span className="font-semibold text-primary">📄 Local Source:</span>
              <p className="text-text-secondary mt-0.5">{conflict.local_claim}</p>
            </div>
            <div className="p-2 rounded bg-bg-card border border-border-light">
              <span className="font-semibold text-amber">🌐 Web Source:</span>
              <p className="text-text-secondary mt-0.5">{conflict.web_claim}</p>
            </div>
          </div>
          <p className="text-[10px] text-text-muted mt-1.5 italic">{conflict.explanation}</p>
        </div>
      ))}
    </div>
  );
}

function renderMessageWithCitations(content: string, citations: Citation[]) {
  if (!citations || citations.length === 0) {
    return <div className="whitespace-pre-wrap leading-relaxed">{content}</div>;
  }

  // Replace [Source: ...] patterns with citation chips
  // Also handle [1], [2] etc. numbered citations
  const parts: (string | React.ReactNode)[] = [];
  let remaining = content;
  let keyId = 0;

  // Match citation patterns like [Source: filename.pdf, p.X] or [1] or [Source: url.com]
  const citationPattern = /\[(?:Source:\s*([^\]]+)|(\d+))\]/g;
  let match;
  let lastIndex = 0;

  while ((match = citationPattern.exec(content)) !== null) {
    // Add text before this match
    if (match.index > lastIndex) {
      parts.push(content.slice(lastIndex, match.index));
    }

    // Find matching citation
    const matchedNum = match[2] ? parseInt(match[2]) : null;
    const matchedSource = match[1] || "";

    let citation: Citation | undefined;
    if (matchedNum !== null) {
      citation = citations.find((c) => c.id === matchedNum);
    } else {
      citation = citations.find(
        (c) =>
          matchedSource.includes(c.source) ||
          (c.title && matchedSource.includes(c.title))
      );
    }

    if (citation) {
      parts.push(<CitationChip key={`cite-${keyId++}`} citation={citation} />);
    } else {
      // Keep original text if no matching citation found
      parts.push(
        <span key={`ref-${keyId++}`} className="text-xs text-text-muted">
          {match[0]}
        </span>
      );
    }

    lastIndex = match.index + match[0].length;
  }

  // Add remaining text
  if (lastIndex < content.length) {
    parts.push(content.slice(lastIndex));
  }

  return <div className="whitespace-pre-wrap leading-relaxed">{parts}</div>;
}

export default function ChatWindow({
  messages,
  isProcessing,
  processingStep,
}: ChatWindowProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isProcessing]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
      {/* Empty state */}
      {messages.length === 0 && !isProcessing && (
        <div className="flex flex-col items-center justify-center h-full text-center max-w-md mx-auto">
          <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-5">
            <span className="text-3xl">🔬</span>
          </div>
          <h2 className="text-xl font-semibold text-text mb-2">
            Welcome to InsightAgent
          </h2>
          <p className="text-sm text-text-secondary leading-relaxed">
            Upload a document or just ask a question — I can search the web too.
            I&apos;ll cite every claim and show you my reasoning step by step.
          </p>
          <div className="flex flex-wrap gap-2 mt-5 justify-center">
            {[
              "What are the key findings in my report?",
              "Compare PDF data with latest web stats",
              "Summarize recent developments in AI",
            ].map((suggestion, i) => (
              <button
                key={i}
                className="px-3 py-1.5 rounded-lg border border-border text-xs text-text-secondary
                  hover:border-primary hover:text-primary hover:bg-primary/5 transition-all"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      {messages.map((msg, index) => (
        <div
          key={index}
          className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} animate-fade-in`}
        >
          <div
            className={`max-w-[75%] rounded-2xl px-4 py-3 ${
              msg.role === "user"
                ? "bg-primary text-white rounded-br-md"
                : "bg-bg-card border border-border shadow-sm rounded-bl-md"
            }`}
          >
            {/* Route indicator for assistant messages */}
            {msg.role === "assistant" && msg.route && (
              <div className="mb-2">
                <RouteIndicator route={msg.route} />
              </div>
            )}

            {/* Message content */}
            <div className={`text-sm ${msg.role === "user" ? "text-white" : "text-text"}`}>
              {msg.role === "assistant"
                ? renderMessageWithCitations(msg.content, msg.citations || [])
                : <p className="whitespace-pre-wrap">{msg.content}</p>
              }
            </div>

            {/* Conflict banners */}
            {msg.role === "assistant" && msg.conflicts && (
              <ConflictBanner conflicts={msg.conflicts} />
            )}

            {/* Citation summary footer */}
            {msg.role === "assistant" && msg.citations && msg.citations.length > 0 && (
              <div className="mt-3 pt-2 border-t border-border-light flex items-center gap-1.5 flex-wrap">
                <span className="text-[10px] text-text-muted">Sources:</span>
                {msg.citations.map((citation) => (
                  <CitationChip key={citation.id} citation={citation} />
                ))}
              </div>
            )}
          </div>
        </div>
      ))}

      {/* Processing indicator */}
      {isProcessing && (
        <div className="flex justify-start animate-fade-in">
          <div className="bg-bg-card border border-border shadow-sm rounded-2xl rounded-bl-md px-4 py-3">
            <div className="flex items-center gap-2 text-sm text-text-secondary">
              <span className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
              <span className="font-mono text-xs">{processingStep || "Thinking..."}</span>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}
