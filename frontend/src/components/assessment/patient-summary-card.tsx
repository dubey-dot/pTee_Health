"use client";

import { useState } from "react";
import { ChevronUp, MessageSquare, Mail } from "lucide-react";

import { cn } from "@/lib/utils";

export interface PatientSummaryField {
  label: string;
  value: string;
}

export interface PatientSummaryCardProps {
  name: string;
  fields: PatientSummaryField[];
  clinicalSummary: string;
  doctorsNotesCount?: number;
  defaultOpen?: boolean;
}

export function PatientSummaryCard({
  name,
  fields,
  clinicalSummary,
  doctorsNotesCount = 0,
  defaultOpen = true,
}: PatientSummaryCardProps) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="rounded-2xl border border-slate-200 bg-white">
      <div className="flex items-center justify-between px-5 py-4">
        <h2 className="text-sm font-semibold text-slate-900">{name}</h2>
        <div className="flex items-center gap-2">
          <button
            type="button"
            aria-label="Email patient"
            className="flex h-8 w-8 items-center justify-center rounded-full border border-slate-200 text-slate-500 transition-colors hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400"
          >
            <Mail className="h-3.5 w-3.5" />
          </button>
          <button
            type="button"
            aria-label="Comment"
            className="flex h-8 w-8 items-center justify-center rounded-full border border-slate-200 text-slate-500 transition-colors hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400"
          >
            <MessageSquare className="h-3.5 w-3.5" />
          </button>
          <button
            type="button"
            aria-expanded={open}
            aria-label={open ? "Collapse patient summary" : "Expand patient summary"}
            onClick={() => setOpen((v) => !v)}
            className="flex h-8 w-8 items-center justify-center rounded-full border border-slate-200 text-slate-500 transition-colors hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400"
          >
            <ChevronUp
              className={cn("h-3.5 w-3.5 transition-transform", !open && "rotate-180")}
            />
          </button>
        </div>
      </div>

      {open && (
        <div className="space-y-5 border-t border-slate-100 px-5 py-5">
          <section>
            <h3 className="text-[11px] font-semibold tracking-wide text-slate-500">
              PATIENT SUMMARY
            </h3>
            <dl className="mt-3 grid grid-cols-[180px_1fr] gap-y-2 text-sm">
              {fields.map((field) => (
                <div key={field.label} className="contents">
                  <dt className="text-slate-500">{field.label}</dt>
                  <dd className="text-slate-900">{field.value || "—"}</dd>
                </div>
              ))}
            </dl>
          </section>

          <section>
            <h3 className="text-[11px] font-semibold tracking-wide text-slate-500">
              CLINICAL SUMMARY
            </h3>
            <p className="mt-3 text-sm leading-6 text-slate-700">{clinicalSummary}</p>
          </section>

          <section>
            <h3 className="text-[11px] font-semibold tracking-wide text-slate-500">
              DOCTOR&apos;S NOTES ({doctorsNotesCount})
            </h3>
            <p className="mt-3 text-sm italic text-slate-400">
              Say &quot;note that…&quot; to dictate a verbatim clinical note.
            </p>
          </section>
        </div>
      )}
    </div>
  );
}
