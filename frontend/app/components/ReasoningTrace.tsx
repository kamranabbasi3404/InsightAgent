"use client";

import { useState } from "react";
import type { TraceStep } from "@/lib/api";

interface ReasoningTraceProps {
  steps: TraceStep[];
  isProcessing: boolean;
}

export default function ReasoningTrace({ steps, isProcessing }: ReasoningTraceProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set());

  const toggleStep = (index: number) => {
    setExpandedSteps((prev) => {
      const next = new Set(prev);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      return next;
    });
  };

  const getStepBorderColor = (step: TraceStep) => {
    if (step.step === "conflict_check" && step.summary.includes("conflict")) {
      return "border-l-conflict";
    }
    if (step.is_retry) return "border-l-amber";
    if (step.step === "grade" && step.summary.includes("insufficient")) return "border-l-amber";
    return "border-l-primary";
  };

  return (
    <div
      className={`flex flex-col border-l border-border bg-bg-sidebar transition-all duration-300 ${
        isCollapsed ? "w-12" : "w-[380px]"
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-3 border-b border-border bg-bg-card/50">
        {!isCollapsed && (
          <div className="flex items-center gap-2">
            <span className="text-sm">🔍</span>
            <h2 className="text-sm font-semibold text-text tracking-tight">Reasoning Trace</h2>
            {isProcessing && (
              <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-primary/10 text-primary text-[10px] font-medium animate-pulse-subtle">
                <span className="w-1.5 h-1.5 rounded-full bg-primary"></span>
                Processing
              </span>
            )}
          </div>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1.5 rounded-md hover:bg-border/50 transition-colors text-text-secondary hover:text-text"
          aria-label={isCollapsed ? "Expand trace panel" : "Collapse trace panel"}
        >
          {isCollapsed ? "◀" : "▶"}
        </button>
      </div>

      {/* Steps */}
      {!isCollapsed && (
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {steps.length === 0 && !isProcessing && (
            <div className="flex flex-col items-center justify-center h-40 text-center">
              <span className="text-2xl mb-2 opacity-40">🧠</span>
              <p className="text-xs text-text-muted">
                Reasoning trace will appear here as the agent processes your query.
              </p>
            </div>
          )}

          {steps.map((step, index) => (
            <div
              key={index}
              className={`animate-slide-in border-l-2 ${getStepBorderColor(step)} rounded-r-lg bg-bg-card
                shadow-sm hover:shadow-md transition-all duration-200 ${
                  step.is_retry ? "ml-4" : ""
                }`}
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <button
                onClick={() => toggleStep(index)}
                className="w-full text-left px-3 py-2.5 flex items-start gap-2"
              >
                <span className="text-sm mt-0.5 flex-shrink-0">{step.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-text font-mono tracking-tight">
                      {step.label}
                    </span>
                    {step.is_retry && (
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-amber/10 text-amber border border-amber/20">
                        RETRY
                      </span>
                    )}
                    {step.step === "conflict_check" && step.summary.includes("conflict") && step.summary.includes("found") && (
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-conflict-light text-conflict border border-conflict/20">
                        ⚠ CONFLICT
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-text-secondary mt-0.5 truncate font-mono">
                    {step.summary}
                  </p>
                </div>
                <span className="text-text-muted text-[10px] mt-1 flex-shrink-0">
                  {expandedSteps.has(index) ? "▼" : "▶"}
                </span>
              </button>

              {expandedSteps.has(index) && (
                <div className="px-3 pb-3 pt-0 animate-fade-in">
                  <div className="p-2 rounded bg-bg-sidebar border border-border-light">
                    <p className="text-[11px] text-text-secondary font-mono leading-relaxed whitespace-pre-wrap">
                      {step.detail}
                    </p>

                    {step.sub_queries && step.sub_queries.length > 0 && (
                      <div className="mt-2 space-y-1">
                        <p className="text-[10px] font-semibold text-text-muted uppercase tracking-wider">
                          Sub-queries:
                        </p>
                        {step.sub_queries.map((sq, i) => (
                          <p key={i} className="text-[11px] text-primary font-mono pl-2 border-l border-primary/30">
                            {sq}
                          </p>
                        ))}
                      </div>
                    )}

                    {step.conflicts && step.conflicts.length > 0 && (
                      <div className="mt-2 space-y-1">
                        {step.conflicts.map((conflict, i) => (
                          <div key={i} className="p-2 rounded bg-conflict-light/50 border border-conflict/20">
                            <p className="text-[10px] font-bold text-conflict">{conflict.topic}</p>
                            <p className="text-[10px] text-text-secondary mt-1">
                              📄 Local: {conflict.local_claim}
                            </p>
                            <p className="text-[10px] text-text-secondary">
                              🌐 Web: {conflict.web_claim}
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}

          {/* Processing shimmer */}
          {isProcessing && (
            <div className="h-12 rounded-lg animate-shimmer border border-border-light" />
          )}
        </div>
      )}
    </div>
  );
}
