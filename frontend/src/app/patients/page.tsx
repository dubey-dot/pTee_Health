import Link from "next/link";
import { UserRound } from "lucide-react";

import { TopNav } from "@/components/layout/top-nav";
import { api } from "@/lib/api";

export default async function PatientsPage() {
  const patients = await api.listPatients();

  return (
    <div className="min-h-full bg-slate-50">
      <TopNav active="Existing Patients" />
      <main className="mx-auto max-w-6xl space-y-4 px-6 py-6">
        <div className="flex items-center justify-between">
          <h1 className="text-sm font-semibold text-slate-900">
            Patients ({patients.length})
          </h1>
          <Link
            href="/patients/new"
            className="rounded-full bg-sky-700 px-4 py-1.5 text-sm font-medium text-white transition-colors hover:bg-sky-800"
          >
            + New patient
          </Link>
        </div>

        <div className="divide-y divide-slate-100 rounded-2xl border border-slate-200 bg-white">
          {patients.length === 0 && (
            <p className="px-5 py-8 text-center text-sm text-slate-500">
              No patients yet — create one to get started.
            </p>
          )}
          {patients.map((patient) => {
            const chiefComplaint = patient.fields.find((f) => f.label === "Chief complaint")?.value;
            return (
              <Link
                key={patient.id}
                href={`/patients/${patient.id}`}
                className="flex items-center gap-3 px-5 py-4 transition-colors hover:bg-slate-50"
              >
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-sky-50 text-sky-600">
                  <UserRound className="h-4 w-4" />
                </span>
                <div className="min-w-0">
                  <p className="text-sm font-medium text-slate-900">{patient.name}</p>
                  {chiefComplaint && (
                    <p className="truncate text-xs text-slate-500">{chiefComplaint}</p>
                  )}
                </div>
              </Link>
            );
          })}
        </div>
      </main>
    </div>
  );
}
