"use client";

import { useState } from "react";
import { Info, Mic, PlayCircle, Trash2 } from "lucide-react";

import { cn } from "@/lib/utils";

export interface FindingDetail {
  question: string;
  bullets: string[];
}

export interface Finding {
  id: string;
  tag: string;
  label: string;
  selected?: boolean;
  detail?: FindingDetail;
}

export interface FindingRowProps {
  finding: Finding;
  onDelete: (id: string) => void;
  onRelabel: (id: string, newLabel: string) => void;
}

export function FindingRow({ finding, onDelete, onRelabel }: FindingRowProps) {
  const [detailOpen, setDetailOpen] = useState(false);
  const [editing, setEditing] = useState(false);
  const [draftLabel, setDraftLabel] = useState(finding.label);
  const [isListening, setIsListening] = useState(false);

  const submitRelabel = () => {
    const trimmed = draftLabel.trim();
    if (trimmed) onRelabel(finding.id, trimmed);
    setEditing(false);
  };

  const iconButtonClass =
    "flex h-7 w-7 items-center justify-center rounded-full text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400";

  return (
    <div
      className={cn(
        finding.selected
          ? "mb-2 rounded-xl border border-sky-200 bg-sky-50 px-4 py-3"
          : "border-b border-slate-100 px-1 py-3 last:border-b-0"
      )}
    >
      <div className="flex items-center justify-between gap-4">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className="shrink-0 rounded-full bg-white px-2 py-0.5 text-[10px] font-semibold tracking-wide text-slate-500 ring-1 ring-slate-200">
              {finding.tag}
            </span>
            {editing ? (
              <input
                autoFocus
                value={draftLabel}
                onChange={(e) => setDraftLabel(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") submitRelabel();
                  if (e.key === "Escape") {
                    setDraftLabel(finding.label);
                    setEditing(false);
                  }
                }}
                onBlur={submitRelabel}
                className="min-w-0 flex-1 rounded-md border border-sky-300 px-2 py-0.5 text-sm font-medium text-slate-900 outline-none focus-visible:ring-2 focus-visible:ring-sky-400"
              />
            ) : (
              <span className="truncate text-sm font-medium text-slate-900">
                {finding.label}
              </span>
            )}
          </div>

          {finding.selected && !editing && (
            <button
              type="button"
              onClick={() => setEditing(true)}
              className="mt-1 flex items-center gap-1 text-xs font-medium text-slate-500 transition-colors hover:text-sky-700"
            >
              <span className="text-sm leading-none">+</span> Type finding instead
            </button>
          )}
        </div>

        <div className="flex shrink-0 items-center gap-1">
          <button
            type="button"
            aria-label="Finding details"
            aria-expanded={detailOpen}
            disabled={!finding.detail}
            onClick={() => setDetailOpen((v) => !v)}
            className={cn(iconButtonClass, !finding.detail && "opacity-40")}
          >
            <Info className="h-3.5 w-3.5" />
          </button>
          <button type="button" aria-label="Play recording" className={iconButtonClass}>
            <PlayCircle className="h-3.5 w-3.5" />
          </button>
          <button
            type="button"
            aria-label="Remove finding"
            onClick={() => onDelete(finding.id)}
            className={iconButtonClass}
          >
            <Trash2 className="h-3.5 w-3.5" />
          </button>
          <button
            type="button"
            aria-pressed={isListening}
            aria-label="Record finding by voice"
            onClick={() => setIsListening((v) => !v)}
            className={cn(
              "flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-white transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400",
              isListening ? "bg-sky-800" : "bg-sky-700 hover:bg-sky-800"
            )}
          >
            <Mic className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {detailOpen && finding.detail && (
        <div className="mt-3 space-y-2 rounded-lg bg-white/60 px-3 py-3">
          <p className="text-sm text-slate-700">{finding.detail.question}</p>
          <ul className="space-y-1">
            {finding.detail.bullets.map((bullet) => (
              <li key={bullet} className="flex items-center gap-2 text-sm text-slate-600">
                <span className="h-1 w-1 shrink-0 rounded-full bg-slate-400" />
                {bullet}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
