"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowRight,
  Check,
  CircleCheck,
  Lightbulb,
  Loader2,
  Pencil,
  RotateCcw,
  Sparkles,
  X,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { FindingsList } from "@/components/assessment/findings-list";
import { RecommendedTestsPanel } from "@/components/assessment/recommended-tests-panel";
import {
  api,
  type Assessment,
  type AssessmentStatus,
  type DiagnosisAction,
  type Finding,
  type Insights,
} from "@/lib/api";
import { cn } from "@/lib/utils";

const DIAGNOSIS_ACTIONS = [
  { value: "agree", label: "Agree", icon: Check },
  { value: "update", label: "Update", icon: Pencil },
  { value: "fully-change", label: "Fully change", icon: RotateCcw },
] as const;

export interface PteeAssistantPanelProps {
  assessmentId: string;
  initialAssessment: Assessment;
  initialFindings: Finding[];
  initialInsights: Insights;
}

export function PteeAssistantPanel({
  assessmentId,
  initialAssessment,
  initialFindings,
  initialInsights,
}: PteeAssistantPanelProps) {
  const queryClient = useQueryClient();
  const [diagnosisOpen, setDiagnosisOpen] = useState(true);
  const assessmentKey = ["assessment", assessmentId];

  const { data: assessment } = useQuery({
    queryKey: assessmentKey,
    queryFn: () => api.getAssessment(assessmentId),
    initialData: initialAssessment,
  });

  const statusMutation = useMutation({
    mutationFn: (status: AssessmentStatus) => api.updateAssessmentStatus(assessmentId, status),
    onSuccess: (updated) => queryClient.setQueryData(assessmentKey, updated),
  });

  const diagnosisActionMutation = useMutation({
    mutationFn: (action: DiagnosisAction) => api.updateDiagnosis(assessmentId, { action }),
    onSuccess: (updated) => queryClient.setQueryData(assessmentKey, updated),
  });

  const generateMutation = useMutation({
    mutationFn: () => api.generateDiagnosis(assessmentId),
    onSuccess: (updated) => {
      queryClient.setQueryData(assessmentKey, updated);
      // Diagnosis generation also (re)writes the insights panel content —
      // refetch it rather than trying to merge partial state in by hand.
      queryClient.invalidateQueries({ queryKey: ["insights", assessmentId] });
    },
  });

  // PTee Assistant starts automatically — no manual "Generate with AI"
  // button. Runs once on mount, and again whenever a test is completed
  // (see onTestCompleted/onTestLogged below) so the cumulative confidence
  // stays current as findings come in. The ref guards against firing
  // twice from React StrictMode's double-invoke in development.
  const hasAutoStarted = useRef(false);
  useEffect(() => {
    if (hasAutoStarted.current) return;
    hasAutoStarted.current = true;
    generateMutation.mutate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [assessmentId]);

  const { status, diagnosis, confidence, diagnosisAction } = assessment;
  const confidenceLabel = confidence >= 60 ? "Good" : confidence >= 40 ? "Fair" : "Low";

  return (
    <div className="rounded-2xl border border-sky-100 bg-white p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3">
          <span className="flex items-center gap-1.5 text-sm font-semibold text-slate-900">
            <Sparkles className="h-4 w-4 text-sky-600" />
            PTee Assistant
          </span>
          {generateMutation.isPending ? (
            <span className="flex items-center gap-1.5 text-[11px] font-semibold tracking-wide text-slate-500">
              <Loader2 className="h-3 w-3 animate-spin text-sky-600" />
              Analyzing…
            </span>
          ) : (
            <span className="flex items-center gap-2 text-[11px] font-semibold tracking-wide text-slate-500">
              CONFIDENCE
              <span className="h-1 w-10 overflow-hidden rounded-full bg-slate-200">
                <span
                  className="block h-full rounded-full bg-sky-600"
                  style={{ width: `${confidence}%` }}
                />
              </span>
              <span className="font-normal text-slate-400">{confidence}%</span>
              <span className="rounded-full bg-sky-50 px-2 py-0.5 text-[11px] font-medium text-sky-700">
                {confidenceLabel}
              </span>
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            className="flex items-center gap-1.5 rounded-full border border-red-200 bg-red-50 px-3.5 py-1.5 text-sm font-medium text-red-600 transition-colors hover:bg-red-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-300"
          >
            <X className="h-3.5 w-3.5" />
            Cancel
          </button>
          <button
            type="button"
            aria-pressed={diagnosisOpen}
            onClick={() => setDiagnosisOpen((v) => !v)}
            className="flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-3.5 py-1.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400"
          >
            <Lightbulb className="h-3.5 w-3.5" />
            Working diagnosis
          </button>
          {status === "reviewing" ? (
            <button
              type="button"
              onClick={() => statusMutation.mutate("completed")}
              className="flex items-center gap-1.5 rounded-full bg-slate-900 px-3.5 py-1.5 text-sm font-medium text-white transition-colors hover:bg-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-400"
            >
              <CircleCheck className="h-3.5 w-3.5" />
              Complete
            </button>
          ) : (
            <span className="flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-3.5 py-1.5 text-sm font-medium text-emerald-700">
              <CircleCheck className="h-3.5 w-3.5" />
              Completed
            </span>
          )}
        </div>
      </div>

      {generateMutation.isError && (
        <p className="mt-3 text-sm text-red-600">
          Couldn&apos;t analyze this assessment. Check the backend has a valid ANTHROPIC_API_KEY
          configured.{" "}
          <button
            type="button"
            onClick={() => generateMutation.mutate()}
            className="font-medium underline hover:no-underline"
          >
            Retry
          </button>
        </p>
      )}

      {diagnosisOpen &&
        (status === "reviewing" ? (
          <div className="mt-4 border-b border-slate-100 pb-4">
            <p className="text-sm font-medium text-sky-700">{diagnosis}</p>
            <div className="mt-3 flex gap-2">
              {DIAGNOSIS_ACTIONS.map((action) => (
                <button
                  key={action.value}
                  type="button"
                  onClick={() => diagnosisActionMutation.mutate(action.value)}
                  className={cn(
                    "flex items-center gap-1.5 rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors",
                    diagnosisAction === action.value
                      ? "border-sky-200 bg-sky-50 text-sky-700"
                      : "border-slate-200 bg-white text-slate-600 hover:bg-slate-50"
                  )}
                >
                  <action.icon className="h-3.5 w-3.5" />
                  {action.label}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="mt-4 flex items-center justify-between rounded-xl bg-emerald-50 px-4 py-3">
            <button
              type="button"
              onClick={() => statusMutation.mutate("reviewing")}
              className="flex items-center gap-1.5 rounded-full border border-emerald-200 bg-white px-3.5 py-1.5 text-sm font-medium text-slate-700 transition-colors hover:bg-emerald-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-300"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              Reopen diagnosis
            </button>
            <button
              type="button"
              className="flex items-center gap-1.5 rounded-full bg-slate-900 px-3.5 py-1.5 text-sm font-medium text-white transition-colors hover:bg-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-400"
            >
              Go to treatment plan
              <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </div>
        ))}

      <RecommendedTestsPanel
        assessmentId={assessmentId}
        onTestCompleted={() => generateMutation.mutate()}
      />

      <div className="mt-4">
        <FindingsList
          assessmentId={assessmentId}
          initialFindings={initialFindings}
          initialInsights={initialInsights}
          onTestLogged={() => generateMutation.mutate()}
        />
      </div>
    </div>
  );
}
