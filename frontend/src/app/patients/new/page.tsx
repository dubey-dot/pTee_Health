import { NewPatientForm } from "@/components/patients/new-patient-form";
import { TopNav } from "@/components/layout/top-nav";

export default function NewPatientPage() {
  return (
    <div className="min-h-full bg-slate-50">
      <TopNav active="New Patients" />
      <main className="mx-auto max-w-6xl px-6 py-6">
        <NewPatientForm />
      </main>
    </div>
  );
}
