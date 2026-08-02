import { AssessmentTabs } from "@/components/assessment/assessment-tabs";
import { PatientSummaryCard } from "@/components/assessment/patient-summary-card";
import { PteeAssistantPanel } from "@/components/assessment/ptee-assistant-panel";
import { TopNav } from "@/components/layout/top-nav";
import { api } from "@/lib/api";
import { DEFAULT_ASSESSMENT_ID, DEFAULT_PATIENT_ID } from "@/lib/constants";

export default async function AssessmentPage() {
  const [patient, assessment, findings, insights] = await Promise.all([
    api.getPatient(DEFAULT_PATIENT_ID),
    api.getAssessment(DEFAULT_ASSESSMENT_ID),
    api.getFindings(DEFAULT_ASSESSMENT_ID),
    api.getInsights(DEFAULT_ASSESSMENT_ID),
  ]);

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
