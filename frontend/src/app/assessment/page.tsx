import { AssessmentScreen } from "@/components/assessment/assessment-screen";
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
    <AssessmentScreen
      patient={patient}
      assessment={assessment}
      findings={findings}
      insights={insights}
    />
  );
}
