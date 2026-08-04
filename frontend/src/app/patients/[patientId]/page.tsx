import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { TopNav } from "@/components/layout/top-nav";
import { NewAssessmentButton } from "@/components/patients/new-assessment-button";
import { api } from "@/lib/api";

export default async function PatientDetailPage({
  params,
}: {
  params: Promise<{ patientId: string }>;
}) {
  const { patientId } = await params;

  const [patient, assessments] = await Promise.all([
    api.getPatient(patientId),
    api.listAssessmentsForPatient(patientId),
  ]);

  return (
    <div className="min-h-full bg-slate-50">
      <TopNav active="Existing Patients" />
      <main className="mx-auto max-w-6xl space-y-4 px-6 py-6">
        <div className="flex items-center justify-between">
          <h1 className="text-sm font-semibold text-slate-900">{patient.name}</h1>
          <NewAssessmentButton patientId={patientId} />
        </div>

        <div className="divide-y divide-slate-100 rounded-2xl border border-slate-200 bg-white">
          {assessments.length === 0 && (
            <p className="px-5 py-8 text-center text-sm text-slate-500">
              No assessments yet for this patient.
            </p>
          )}
          {assessments.map((assessment) => (
            <Link
              key={assessment.id}
              href={`/assessment/${assessment.id}`}
              className="flex items-center justify-between gap-3 px-5 py-4 transition-colors hover:bg-slate-50"
            >
              <div>
                <p className="text-sm font-medium text-slate-900">
                  {assessment.diagnosis || "Working diagnosis pending"}
                </p>
                <p className="mt-0.5 text-xs text-slate-500">
                  Status: {assessment.status} · Confidence: {assessment.confidence}%
                </p>
              </div>
              <ArrowRight className="h-3.5 w-3.5 shrink-0 text-slate-400" />
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
