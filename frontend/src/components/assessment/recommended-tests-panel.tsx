"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Check,
  ChevronDown,
  ClipboardList,
  Loader2,
  Mic,
  Pencil,
  RotateCcw,
  Sparkles,
  Square,
  Trash2,
  X,
} from "lucide-react";

import { api, type LoggedTest, type RecommendedTest } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useVoiceDictation } from "@/lib/use-voice-dictation";

export interface RecommendedTestsPanelProps {
  assessmentId: string;
  /** Called after a recommended test is completed (real findings saved) so
   * the parent can re-trigger diagnosis generation with the new data. */
  onTestCompleted?: () => void;
}

function PendingTestCard({
  test,
  onDelete,
  onComplete,
  isCompleting,
}: {
  test: RecommendedTest;
  onDelete: () => void;
  onComplete: (result: string) => void;
  isCompleting: boolean;
}) {
  const [expanded, setExpanded] = useState(false);
  const [findings, setFindings] = useState("");
  const { isListening, voiceError, toggleListening } = useVoiceDictation((transcript) =>
    setFindings((prev) => (prev ? `${prev.trim()} ${transcript}` : transcript))
  );

  const canComplete = findings.trim().length > 0 && !isCompleting;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <h4 className="text-sm font-semibold text-slate-900">{test.testName}</h4>
          <p className="mt-0.5 text-sm text-slate-500">{test.summary}</p>
        </div>
        <button
          type="button"
          onClick={onDelete}
          aria-label="Delete recommendation"
          className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-slate-400 transition-colors hover:bg-slate-100 hover:text-red-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400"
        >
          <Trash2 className="h-3.5 w-3.5" />
        </button>
      </div>

      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        aria-expanded={expanded}
        className="mt-2 flex items-center gap-1 text-xs font-medium text-sky-700 hover:underline"
      >
        <Sparkles className="h-3 w-3" />
        Why this test
        <ChevronDown className={cn("h-3 w-3 transition-transform", expanded && "rotate-180")} />
      </button>
      {expanded && (
        <p className="mt-2 rounded-lg bg-slate-50 p-2.5 text-xs text-slate-600">
          {test.whyRecommended}
        </p>
      )}

      <div className="mt-3 border-t border-slate-100 pt-3">
        <label className="text-[11px] font-semibold tracking-wide text-slate-500">FINDINGS</label>
        <div className="mt-1.5 flex items-start gap-2 rounded-xl border border-slate-200 py-2 pr-2 pl-3.5 focus-within:border-sky-300 focus-within:ring-3 focus-within:ring-sky-100">
          <textarea
            value={findings}
            onChange={(e) => setFindings(e.target.value)}
            placeholder="Write or dictate what you found…"
            rows={2}
            className="min-h-[2.5rem] flex-1 resize-none bg-transparent py-1.5 text-sm text-slate-900 placeholder:italic placeholder:text-slate-400 outline-none"
          />
          <button
            type="button"
            onClick={toggleListening}
            aria-pressed={isListening}
            aria-label={isListening ? "Stop dictating findings" : "Dictate findings by voice"}
            className={cn(
              "mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-white transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400",
              isListening ? "bg-sky-800" : "bg-sky-700 hover:bg-sky-800"
            )}
          >
            {isListening ? <Square className="h-3 w-3" /> : <Mic className="h-3.5 w-3.5" />}
          </button>
        </div>
        {voiceError && (
          <p className="mt-1.5 text-[11px] text-red-600">
            Voice input isn&apos;t supported in this browser — try Chrome or Edge, or type instead.
          </p>
        )}
        <div className="mt-2 flex justify-end">
          <button
            type="button"
            onClick={() => onComplete(findings.trim())}
            disabled={!canComplete}
            className="flex items-center gap-1.5 rounded-full bg-emerald-600 px-3.5 py-1.5 text-xs font-medium text-white transition-colors hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {isCompleting ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Check className="h-3.5 w-3.5" />
            )}
            Mark complete
          </button>
        </div>
      </div>
    </div>
  );
}

function CompletedTestRow({
  test,
  onSave,
  isSaving,
}: {
  test: LoggedTest;
  onSave: (result: string) => void;
  isSaving: boolean;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(test.result);

  if (!editing) {
    return (
      <li className="rounded-lg border border-slate-100 bg-slate-50 px-3 py-2">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <p className="text-sm font-medium text-slate-900">{test.name}</p>
            <p className="mt-0.5 text-xs text-slate-600">{test.result || "(no findings recorded)"}</p>
          </div>
          <button
            type="button"
            onClick={() => {
              setDraft(test.result);
              setEditing(true);
            }}
            className="flex shrink-0 items-center gap-1 text-xs font-medium text-sky-700 hover:underline"
          >
            <Pencil className="h-3 w-3" />
            Edit
          </button>
        </div>
      </li>
    );
  }

  return (
    <li className="rounded-lg border border-sky-200 bg-white px-3 py-2">
      <p className="text-sm font-medium text-slate-900">{test.name}</p>
      <textarea
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        rows={2}
        className="mt-1.5 w-full resize-none rounded-lg border border-slate-200 px-2.5 py-1.5 text-xs text-slate-900 outline-none focus:border-sky-300"
      />
      <div className="mt-1.5 flex justify-end gap-2">
        <button
          type="button"
          onClick={() => setEditing(false)}
          className="flex items-center gap-1 text-xs font-medium text-slate-500 hover:text-slate-700"
        >
          <X className="h-3 w-3" />
          Cancel
        </button>
        <button
          type="button"
          onClick={() => {
            onSave(draft.trim());
            setEditing(false);
          }}
          disabled={!draft.trim() || isSaving}
          className="flex items-center gap-1 rounded-full bg-sky-700 px-3 py-1 text-xs font-medium text-white transition-colors hover:bg-sky-800 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          <Check className="h-3 w-3" />
          Save
        </button>
      </div>
    </li>
  );
}

/** PTee Assistant's core recommendation surface: a reviewable feed of up
 * to 4 AI-recommended tests. Each pending test can be deleted, or
 * completed by writing/dictating findings directly — completing creates
 * a real logged test (no separate accept step). Completed tests are the
 * actual backend `tests` list for this assessment (shared with the
 * separate "Log a test" flow), editable in place. */
export function RecommendedTestsPanel({ assessmentId, onTestCompleted }: RecommendedTestsPanelProps) {
  const queryClient = useQueryClient();
  const testsKey = ["tests", assessmentId];
  const [pendingTests, setPendingTests] = useState<RecommendedTest[] | null>(null);

  const { data: completedTests = [] } = useQuery({
    queryKey: testsKey,
    queryFn: () => api.getTests(assessmentId),
  });

  const suggestMutation = useMutation({
    mutationFn: () => api.getTestRecommendations(assessmentId),
    onSuccess: (batch) => setPendingTests(batch.tests),
  });

  const [completingIndex, setCompletingIndex] = useState<number | null>(null);
  const completeMutation = useMutation({
    mutationFn: (params: { index: number; test: RecommendedTest; result: string }) =>
      api.createTest(assessmentId, {
        type: params.test.testType,
        name: params.test.testName,
        result: params.result,
      }),
    onMutate: (params) => setCompletingIndex(params.index),
    onSuccess: (created, params) => {
      queryClient.setQueryData<LoggedTest[]>(testsKey, (prev) => [...(prev ?? []), created]);
      setPendingTests((prev) => (prev ? prev.filter((_, i) => i !== params.index) : prev));
      onTestCompleted?.();
    },
    onSettled: () => setCompletingIndex(null),
  });

  const updateMutation = useMutation({
    mutationFn: (params: { id: string; result: string }) => api.updateTest(params.id, params.result),
    onSuccess: (updated) => {
      queryClient.setQueryData<LoggedTest[]>(testsKey, (prev) =>
        (prev ?? []).map((t) => (t.id === updated.id ? updated : t))
      );
      onTestCompleted?.();
    },
  });

  const noRecommendationReason = suggestMutation.data?.noRecommendationReason ?? null;

  const deleteRecommendation = (index: number) =>
    setPendingTests((prev) => (prev ? prev.filter((_, i) => i !== index) : prev));

  return (
    <div className="mt-4 border-t border-slate-100 pt-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="flex items-center gap-1.5 text-sm font-semibold text-slate-900">
            <Sparkles className="h-3.5 w-3.5 text-sky-600" />
            Recommended tests
          </h3>
          <p className="mt-0.5 text-xs text-slate-500">Based on intake notes</p>
        </div>
        <button
          type="button"
          onClick={() => suggestMutation.mutate()}
          disabled={suggestMutation.isPending}
          className="flex shrink-0 items-center gap-1.5 rounded-full border border-slate-200 bg-white px-3.5 py-1.5 text-xs font-medium text-slate-700 transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {suggestMutation.isPending ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <RotateCcw className="h-3.5 w-3.5" />
          )}
          {pendingTests ? "Reset review" : "Suggest tests"}
        </button>
      </div>

      {suggestMutation.isError && (
        <p className="mt-3 text-sm text-red-600">
          Couldn&apos;t get recommendations. Check the backend has a valid ANTHROPIC_API_KEY
          configured and try again.
        </p>
      )}

      {pendingTests && pendingTests.length === 0 && (
        <p className="mt-3 text-sm text-slate-600">
          {noRecommendationReason ?? "No further tests are recommended right now."}
        </p>
      )}

      {pendingTests && pendingTests.length > 0 && (
        <div className="mt-3 space-y-3">
          {pendingTests.map((test, i) => (
            <PendingTestCard
              key={i}
              test={test}
              onDelete={() => deleteRecommendation(i)}
              onComplete={(result) => completeMutation.mutate({ index: i, test, result })}
              isCompleting={completingIndex === i && completeMutation.isPending}
            />
          ))}
        </div>
      )}

      <div className="mt-4 rounded-xl border border-slate-200 bg-white p-4">
        <div className="flex items-center justify-between">
          <h4 className="flex items-center gap-1.5 text-sm font-semibold text-slate-900">
            <ClipboardList className="h-3.5 w-3.5 text-slate-500" />
            Completed tests
          </h4>
          <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-slate-100 px-1.5 text-xs font-medium text-slate-600">
            {completedTests.length}
          </span>
        </div>
        {completedTests.length === 0 ? (
          <p className="mt-2 text-xs text-slate-400">
            Tests you complete will appear here with their results.
          </p>
        ) : (
          <ul className="mt-2 space-y-1.5">
            {completedTests.map((test) => (
              <CompletedTestRow
                key={test.id}
                test={test}
                onSave={(result) => updateMutation.mutate({ id: test.id, result })}
                isSaving={updateMutation.isPending && updateMutation.variables?.id === test.id}
              />
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
