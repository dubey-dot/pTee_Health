"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Check, ChevronDown, ClipboardList, Loader2, RotateCcw, Sparkles, X } from "lucide-react";

import { api, type RecommendedTest } from "@/lib/api";
import { cn } from "@/lib/utils";

export interface RecommendedTestsPanelProps {
  assessmentId: string;
}

type Decision = "pending" | "accepted" | "rejected";

interface Entry {
  test: RecommendedTest;
  status: Decision;
}

function confidenceMeta(confidence: number) {
  if (confidence >= 70) {
    return { label: "High confidence", bar: "bg-emerald-500", text: "text-emerald-700" };
  }
  if (confidence >= 45) {
    return { label: "Medium confidence", bar: "bg-amber-500", text: "text-amber-700" };
  }
  return { label: "Low confidence", bar: "bg-red-500", text: "text-red-600" };
}

/** PTee Assistant's core recommendation surface: a reviewable feed of up
 * to 4 AI-recommended tests (recommendation_rules.md Rule 1), each with
 * its own confidence score and expandable reasoning. Accept/Reject state
 * is client-side only — nothing is persisted until the doctor actually
 * logs a performed test through the existing "Log a test" flow. */
export function RecommendedTestsPanel({ assessmentId }: RecommendedTestsPanelProps) {
  const [entries, setEntries] = useState<Entry[] | null>(null);
  const [expanded, setExpanded] = useState<Set<number>>(new Set());
  const [lastRejected, setLastRejected] = useState<number | null>(null);

  const mutation = useMutation({
    mutationFn: () => api.getTestRecommendations(assessmentId),
    onSuccess: (batch) => {
      setEntries(batch.tests.map((test) => ({ test, status: "pending" as Decision })));
      setExpanded(new Set());
      setLastRejected(null);
    },
  });

  const noRecommendationReason = mutation.data?.noRecommendationReason ?? null;

  const toggleExpanded = (i: number) =>
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(i)) next.delete(i);
      else next.add(i);
      return next;
    });

  const setStatus = (i: number, status: Decision) => {
    setEntries((prev) => prev && prev.map((e, idx) => (idx === i ? { ...e, status } : e)));
    setLastRejected(status === "rejected" ? i : null);
  };

  const undoReject = () => {
    if (lastRejected === null) return;
    setStatus(lastRejected, "pending");
  };

  const pending = entries?.filter((e) => e.status === "pending") ?? [];
  const accepted = entries?.filter((e) => e.status === "accepted") ?? [];
  const total = entries?.length ?? 0;

  return (
    <div className="mt-4 border-t border-slate-100 pt-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="flex items-center gap-1.5 text-sm font-semibold text-slate-900">
            <Sparkles className="h-3.5 w-3.5 text-sky-600" />
            Recommended tests
          </h3>
          <p className="mt-0.5 text-xs text-slate-500">Based on intake notes</p>
          {entries && entries.length > 0 && (
            <p className="mt-1 text-xs font-medium text-slate-600">
              {pending.length} of {total} tests awaiting your review
            </p>
          )}
        </div>
        <button
          type="button"
          onClick={() => mutation.mutate()}
          disabled={mutation.isPending}
          className="flex shrink-0 items-center gap-1.5 rounded-full border border-slate-200 bg-white px-3.5 py-1.5 text-xs font-medium text-slate-700 transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {mutation.isPending ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <RotateCcw className="h-3.5 w-3.5" />
          )}
          {entries ? "Reset review" : "Suggest tests"}
        </button>
      </div>

      {mutation.isError && (
        <p className="mt-3 text-sm text-red-600">
          Couldn&apos;t get recommendations. Check the backend has a valid ANTHROPIC_API_KEY
          configured and try again.
        </p>
      )}

      {entries && entries.length === 0 && (
        <p className="mt-3 text-sm text-slate-600">
          {noRecommendationReason ?? "No further tests are recommended right now."}
        </p>
      )}

      {lastRejected !== null && (
        <div className="mt-3 flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-xs text-slate-600">
          <span>Test rejected.</span>
          <button
            type="button"
            onClick={undoReject}
            className="font-medium text-sky-700 hover:underline"
          >
            Undo
          </button>
        </div>
      )}

      {pending.length > 0 && (
        <div className="mt-3 space-y-3">
          {entries?.map((entry, i) => {
            if (entry.status !== "pending") return null;
            const meta = confidenceMeta(entry.test.confidence);
            const isExpanded = expanded.has(i);
            return (
              <div key={i} className="rounded-xl border border-slate-200 bg-white p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <h4 className="text-sm font-semibold text-slate-900">
                      {entry.test.testName}
                    </h4>
                    <p className="mt-0.5 text-sm text-slate-500">{entry.test.summary}</p>
                  </div>
                  <div className="w-28 shrink-0 text-right">
                    <div className="flex items-center gap-2">
                      <span className="h-1.5 w-16 overflow-hidden rounded-full bg-slate-200">
                        <span
                          className={cn("block h-full rounded-full", meta.bar)}
                          style={{ width: `${entry.test.confidence}%` }}
                        />
                      </span>
                      <span className="text-xs font-semibold text-slate-700">
                        {entry.test.confidence}%
                      </span>
                    </div>
                    <p className={cn("mt-0.5 text-[11px]", meta.text)}>{meta.label}</p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => toggleExpanded(i)}
                  aria-expanded={isExpanded}
                  className="mt-2 flex items-center gap-1 text-xs font-medium text-sky-700 hover:underline"
                >
                  <Sparkles className="h-3 w-3" />
                  Why this test
                  <ChevronDown
                    className={cn("h-3 w-3 transition-transform", isExpanded && "rotate-180")}
                  />
                </button>

                {isExpanded && (
                  <p className="mt-2 rounded-lg bg-slate-50 p-2.5 text-xs text-slate-600">
                    {entry.test.whyRecommended}
                  </p>
                )}

                <div className="mt-3 flex gap-2">
                  <button
                    type="button"
                    onClick={() => setStatus(i, "accepted")}
                    className="flex items-center gap-1.5 rounded-full bg-emerald-600 px-3.5 py-1.5 text-xs font-medium text-white transition-colors hover:bg-emerald-700"
                  >
                    <Check className="h-3.5 w-3.5" />
                    Accept
                  </button>
                  <button
                    type="button"
                    onClick={() => setStatus(i, "rejected")}
                    className="flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-3.5 py-1.5 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-50"
                  >
                    <X className="h-3.5 w-3.5" />
                    Reject
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {entries && entries.length > 0 && (
        <div className="mt-4 rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex items-center justify-between">
            <h4 className="flex items-center gap-1.5 text-sm font-semibold text-slate-900">
              <ClipboardList className="h-3.5 w-3.5 text-slate-500" />
              Selected tests
            </h4>
            <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-slate-100 px-1.5 text-xs font-medium text-slate-600">
              {accepted.length}
            </span>
          </div>
          {accepted.length === 0 ? (
            <p className="mt-2 text-xs text-slate-400">
              Accepted tests will appear here for you to review before adding them to the plan.
            </p>
          ) : (
            <ul className="mt-2 space-y-1.5">
              {accepted.map((entry, i) => (
                <li key={i} className="flex items-center justify-between text-sm text-slate-700">
                  <span>{entry.test.testName}</span>
                  <span className="text-xs text-slate-400">{entry.test.confidence}%</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
