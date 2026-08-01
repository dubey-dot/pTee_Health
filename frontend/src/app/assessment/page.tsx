import { AssessmentTabs } from "@/components/assessment/assessment-tabs";
import { PatientSummaryCard } from "@/components/assessment/patient-summary-card";
import { PteeAssistantPanel } from "@/components/assessment/ptee-assistant-panel";
import { TopNav } from "@/components/layout/top-nav";

const PATIENT_FIELDS = [
  { label: "Name", value: "Ankita Sharma" },
  { label: "Age / Gender", value: "32 · Female" },
  { label: "Occupation / Sport", value: "a software engineer and i · runner" },
  { label: "Chief complaint", value: "Right anterior knee pain" },
  { label: "Duration", value: "3 months" },
  { label: "Pain score", value: "" },
  { label: "Aggravating", value: "stairs, squatting, better with rest, ice" },
  { label: "Relieving", value: "rest, ice" },
  { label: "Previous injuries", value: "" },
];

const CLINICAL_SUMMARY =
  "Presenting with right anterior knee pain for 3 months. Findings so far involve Pelvis, Hip, Ankle, with pelvis anterior; hip restricted; ankle limited. Muscle picture: Glute Med (overactive), Tfl (overactive), Quad (weak), Hamstring (weak).";

export default function AssessmentPage() {
  return (
    <div className="min-h-full bg-slate-50">
      <TopNav />
      <main className="mx-auto max-w-6xl space-y-4 px-6 py-6">
        <AssessmentTabs />
        <PatientSummaryCard
          name="Ankita Sharma"
          fields={PATIENT_FIELDS}
          clinicalSummary={CLINICAL_SUMMARY}
          doctorsNotesCount={0}
        />
        <PteeAssistantPanel />
      </main>
    </div>
  );
}
