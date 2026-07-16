"use client";

import { useState, useCallback } from "react";
import { uploadPDF, getDocuments, deleteDocument } from "@/lib/api";
import type { DocumentInfo } from "@/lib/api";

interface UploadPanelProps {
  documents: DocumentInfo[];
  onDocumentsChange: () => void;
  isOpen: boolean;
  onClose: () => void;
}

export default function UploadPanel({
  documents,
  onDocumentsChange,
  isOpen,
  onClose,
}: UploadPanelProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleUpload = useCallback(
    async (file: File) => {
      if (!file.name.toLowerCase().endsWith(".pdf")) {
        setUploadError("Only PDF files are supported.");
        return;
      }

      setUploadError(null);
      setUploadProgress("Uploading...");

      try {
        setUploadProgress("Parsing PDF...");
        const result = await uploadPDF(file);
        setUploadProgress(null);
        onDocumentsChange();
        setUploadError(null);
      } catch (err) {
        setUploadProgress(null);
        setUploadError(err instanceof Error ? err.message : "Upload failed");
      }
    },
    [onDocumentsChange]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleUpload(file);
    },
    [handleUpload]
  );

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleUpload(file);
      e.target.value = ""; // Reset for re-upload of same file
    },
    [handleUpload]
  );

  const handleDelete = async (filename: string) => {
    try {
      await deleteDocument(filename);
      onDocumentsChange();
    } catch {
      setUploadError("Failed to delete document");
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
      <div className="bg-bg-card rounded-xl shadow-2xl border border-border w-full max-w-lg mx-4 animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-border">
          <div>
            <h2 className="text-lg font-semibold text-text">Document Manager</h2>
            <p className="text-xs text-text-secondary mt-0.5">
              Upload PDFs to build your local knowledge base
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-bg-sidebar transition-colors text-text-secondary hover:text-text"
            aria-label="Close upload panel"
          >
            ✕
          </button>
        </div>

        {/* Drop Zone */}
        <div className="p-5">
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200
              ${
                isDragging
                  ? "border-primary bg-primary/5 scale-[1.02]"
                  : "border-border hover:border-primary/50 hover:bg-bg-sidebar/50"
              }`}
          >
            <div className="text-3xl mb-3 opacity-60">📁</div>
            <p className="text-sm font-medium text-text">
              Drop a PDF here, or{" "}
              <label className="text-primary cursor-pointer hover:underline">
                browse
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileSelect}
                  className="hidden"
                />
              </label>
            </p>
            <p className="text-xs text-text-muted mt-1">PDF files only, up to 50MB</p>

            {uploadProgress && (
              <div className="mt-4 flex items-center justify-center gap-2 text-primary text-sm">
                <span className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                {uploadProgress}
              </div>
            )}
          </div>

          {uploadError && (
            <div className="mt-3 p-3 rounded-lg bg-conflict-light border border-conflict/20 text-conflict text-xs">
              ⚠ {uploadError}
            </div>
          )}
        </div>

        {/* Document List */}
        <div className="px-5 pb-5">
          <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">
            Indexed Documents ({documents.length})
          </h3>

          {documents.length === 0 ? (
            <div className="text-center py-6 text-text-muted text-xs">
              No documents indexed yet. Upload a PDF to get started.
            </div>
          ) : (
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {documents.map((doc) => (
                <div
                  key={doc.filename}
                  className="flex items-center justify-between p-3 rounded-lg bg-bg-sidebar border border-border-light
                    hover:border-border transition-colors group"
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <span className="text-primary text-sm flex-shrink-0">📄</span>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-text truncate">{doc.filename}</p>
                      <p className="text-[10px] text-text-muted">{doc.chunk_count} chunks</p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDelete(doc.filename)}
                    className="opacity-0 group-hover:opacity-100 p-1.5 rounded-md hover:bg-conflict-light
                      text-text-muted hover:text-conflict transition-all text-xs"
                    aria-label={`Delete ${doc.filename}`}
                  >
                    🗑
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
