"use client";

import { useState } from "react";
import type { Citation } from "@/lib/api";

interface CitationChipProps {
  citation: Citation;
}

export default function CitationChip({ citation }: CitationChipProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const isPdf = citation.type === "pdf";
  const bgColor = isPdf
    ? "bg-primary/10 hover:bg-primary/20 text-primary"
    : "bg-amber/10 hover:bg-amber/20 text-amber";
  const borderColor = isPdf ? "border-primary/30" : "border-amber/30";
  const icon = isPdf ? "📄" : "🌐";

  const label = isPdf
    ? `${citation.source}${citation.page ? `, p.${citation.page}` : ""}`
    : citation.title || citation.source;

  return (
    <span className="relative inline-block">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium 
          border ${borderColor} ${bgColor} transition-all duration-200 cursor-pointer
          hover:shadow-sm`}
        aria-label={`Citation: ${label}`}
      >
        <span className="text-[10px]">{icon}</span>
        <span className="max-w-[120px] truncate">[{citation.id}]</span>
      </button>

      {isExpanded && (
        <div
          className={`absolute z-50 bottom-full left-0 mb-2 w-80 p-3 rounded-lg shadow-lg border
            ${borderColor} bg-bg-card animate-fade-in`}
        >
          <div className="flex items-center gap-2 mb-2">
            <span>{icon}</span>
            <span className={`text-sm font-semibold ${isPdf ? "text-primary" : "text-amber"}`}>
              {isPdf ? "PDF Source" : "Web Source"}
            </span>
          </div>

          <div className="text-xs space-y-1">
            <p className="font-medium text-text">
              {isPdf ? citation.source : citation.title || "Web Result"}
            </p>

            {isPdf && citation.page && (
              <p className="text-text-secondary">Page {citation.page}</p>
            )}

            {!isPdf && citation.source && (
              <a
                href={citation.source}
                target="_blank"
                rel="noopener noreferrer"
                className="text-amber hover:underline break-all"
              >
                {citation.source}
              </a>
            )}

            {citation.snippet && (
              <div className="mt-2 p-2 rounded bg-bg-sidebar text-text-secondary text-[11px] leading-relaxed border border-border-light">
                &quot;{citation.snippet}&quot;
              </div>
            )}
          </div>

          <button
            onClick={() => setIsExpanded(false)}
            className="absolute top-2 right-2 text-text-muted hover:text-text text-xs"
            aria-label="Close citation"
          >
            ✕
          </button>
        </div>
      )}
    </span>
  );
}
