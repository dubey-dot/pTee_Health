"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { useState } from "react";

import { FindingRow } from "@/components/assessment/finding-row";
import { InsightsPanel } from "@/components/assessment/insights-panel";
import { LogTestPanel } from "@/components/assessment/log-test-panel";
import { api, type Finding, type Insights, type TestType } from "@/lib/api";

export interface FindingsListProps {
  assessmentId: string;
  initialFindings: Finding[];
  initialInsights: Insights;
  /** Called after a test is logged so the parent can re-trigger diagnosis
   * generation with the new data. */
  onTestLogged?: () => void;
}

export function FindingsList({
  assessmentId,
  initialFindings,
  initialInsights,
  onTestLogged,
}: FindingsListProps) {
  const queryClient = useQueryClient();
  const [showLogTest, setShowLogTest] = useState(false);
  const findingsKey = ["findings", assessmentId];

  const { data: findings = [] } = useQuery({
    queryKey: findingsKey,
    queryFn: () => api.getFindings(assessmentId),
    initialData: initialFindings,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.deleteFinding(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: findingsKey });
      const previous = queryClient.getQueryData<Finding[]>(findingsKey);
      queryClient.setQueryData<Finding[]>(findingsKey, (prev) =>
        (prev ?? []).filter((f) => f.id !== id)
      );
      return { previous };
    },
    onError: (_err, _id, context) => {
      if (context?.previous) queryClient.setQueryData(findingsKey, context.previous);
    },
    onSettled: () => queryClient.invalidateQueries({ queryKey: findingsKey }),
  });

  const relabelMutation = useMutation({
    mutationFn: ({ id, label }: { id: string; label: string }) => api.updateFinding(id, label),
    onMutate: async ({ id, label }) => {
      await queryClient.cancelQueries({ queryKey: findingsKey });
      const previous = queryClient.getQueryData<Finding[]>(findingsKey);
      queryClient.setQueryData<Finding[]>(findingsKey, (prev) =>
        (prev ?? []).map((f) => (f.id === id ? { ...f, label } : f))
      );
      return { previous };
    },
    onError: (_err, _vars, context) => {
      if (context?.previous) queryClient.setQueryData(findingsKey, context.previous);
    },
    onSettled: () => queryClient.invalidateQueries({ queryKey: findingsKey }),
  });

  const testMutation = useMutation({
    mutationFn: (test: { type: TestType; name: string; result: string }) =>
      api.createTest(assessmentId, test),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["insights", assessmentId] });
      queryClient.invalidateQueries({ queryKey: ["tests", assessmentId] });
      setShowLogTest(false);
      onTestLogged?.();
    },
  });

  return (
    <div className="space-y-2">
      {findings.map((finding) => (
        <FindingRow
          key={finding.id}
          finding={finding}
          onDelete={(id) => deleteMutation.mutate(id)}
          onRelabel={(id, label) => relabelMutation.mutate({ id, label })}
        />
      ))}

      {showLogTest ? (
        <LogTestPanel
          onClose={() => setShowLogTest(false)}
          onSave={(test) => testMutation.mutate(test)}
        />
      ) : (
        <button
          type="button"
          onClick={() => setShowLogTest(true)}
          className="flex w-full items-center justify-center gap-1.5 rounded-xl border border-dashed border-sky-200 py-3 text-sm font-medium text-sky-700 transition-colors hover:bg-sky-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400"
        >
          <Plus className="h-3.5 w-3.5" />
          Log a test
        </button>
      )}

      <InsightsPanel assessmentId={assessmentId} initialInsights={initialInsights} />
    </div>
  );
}
