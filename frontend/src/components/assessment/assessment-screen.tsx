import { AssessmentTabs } from "@/components/assessment/assessment-tabs";
import { PatientSummaryCard } from "@/components/assessment/patient-summary-card";
import { PteeAssistantPanel } from "@/components/assessment/ptee-assistant-panel";
import { TopNav } from "@/components/layout/top-nav";
import type { Assessment, Finding, Insights, PatientSummary } from "@/lib/api";

export interface AssessmentScreenProps {
  patient: PatientSummary;
  assessment: Assessment;
  findings: Finding[];
  insights: Insights;
}

/** Shared render for any assessment — used by both the fixed demo route
 * (`/assessment`) and the per-assessment dynamic route
 * (`/assessment/[assessmentId]`), which differ only in how they fetch the
 * four pieces of data above. */
export function AssessmentScreen({
  patient,
  assessment,
  findings,
  insights,
}: AssessmentScreenProps) {
  return (
    <div className="min-h-full bg-slate-50">
      <TopNav />
      <main className="mx-auto max-w-6xl space-y-4 px-6 py-6">
        <AssessmentTabs />
        <PatientSummaryCard
          name={patient.name}
          fields={patient.fields}
          clinicalSummary={patient.clinicalSummary}
          doctorsNotesCount={patient.doctorsNotesCount}
        />
        <PteeAssistantPanel
          assessmentId={assessment.id}
          initialAssessment={assessment}
          initialFindings={findings}
          initialInsights={insights}
        />
      </main>
    </div>
  );
}
