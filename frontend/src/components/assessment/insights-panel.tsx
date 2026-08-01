"use client";

import { useState } from "react";
import { ChevronDown, Sparkles } from "lucide-react";

import { cn } from "@/lib/utils";

export interface InsightTag {
  label: string;
  meta: string;
}

export interface InsightsPanelProps {
  summary?: string;
  tags?: InsightTag[];
  defaultOpen?: boolean;
}

const DEFAULT_SUMMARY =
  "Biceps Femoris: Quad — weak. Next, Pelvis Shift Right/Left. A lateral pelvic shift changes hip loading and frontal-plane control.";

const DEFAULT_TAGS: InsightTag[] = [
  { label: "Biceps Femoris — Quad — weak", meta: "8 recorded" },
];

export function InsightsPanel({
  summary = DEFAULT_SUMMARY,
  tags = DEFAULT_TAGS,
  defaultOpen = true,
}: InsightsPanelProps) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="rounded-2xl border border-sky-100 bg-sky-50/60">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="flex w-full items-center justify-between px-5 py-4 text-left focus-visible:outline-none"
      >
        <span className="flex items-center gap-2 text-sm font-semibold text-slate-900">
          <Sparkles className="h-4 w-4 text-sky-600" />
          Insights
        </span>
        <ChevronDown
          className={cn(
            "h-4 w-4 text-slate-500 transition-transform",
            open ? "rotate-0" : "-rotate-90"
          )}
        />
      </button>

      {open && (
        <div className="space-y-3 px-5 pb-5">
          <p className="text-sm leading-6 text-slate-700">{summary}</p>

          {tags.map((tag) => (
            <div
              key={tag.label}
              className="flex items-center justify-between rounded-full bg-white px-4 py-2"
            >
              <span className="flex items-center gap-2 text-sm text-slate-800">
                <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-sky-500" />
                {tag.label}
              </span>
              <span className="shrink-0 rounded-full bg-sky-100 px-2.5 py-0.5 text-xs font-medium text-sky-700">
                {tag.meta}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
