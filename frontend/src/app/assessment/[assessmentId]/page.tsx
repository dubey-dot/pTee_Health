import { AssessmentScreen } from "@/components/assessment/assessment-screen";
import { api } from "@/lib/api";

export default async function AssessmentByIdPage({
  params,
}: {
  params: Promise<{ assessmentId: string }>;
}) {
  const { assessmentId } = await params;

  const assessment = await api.getAssessment(assessmentId);
  const [patient, findings, insights] = await Promise.all([
    api.getPatient(assessment.patientId),
    api.getFindings(assessmentId),
    api.getInsights(assessmentId),
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
