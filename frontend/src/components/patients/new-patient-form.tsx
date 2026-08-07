"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { api, type PatientCreateInput } from "@/lib/api";

type FormState = {
  name: string;
  age: string;
  gender: string;
  occupationSport: string;
  chiefComplaint: string;
  duration: string;
  painScore: string;
  aggravating: string;
  relieving: string;
  previousInjuries: string;
};

const EMPTY_FORM: FormState = {
  name: "",
  age: "",
  gender: "",
  occupationSport: "",
  chiefComplaint: "",
  duration: "",
  painScore: "",
  aggravating: "",
  relieving: "",
  previousInjuries: "",
};

const FIELDS: {
  key: keyof FormState;
  label: string;
  placeholder?: string;
  type?: string;
  multiline?: boolean;
}[] = [
  { key: "age", label: "Age", type: "number", placeholder: "e.g. 32" },
  { key: "gender", label: "Gender", placeholder: "e.g. Female" },
  { key: "occupationSport", label: "Occupation / Sport", placeholder: "e.g. Software engineer · runner" },
  { key: "duration", label: "Duration", placeholder: "e.g. 3 months" },
  { key: "painScore", label: "Pain score", placeholder: "e.g. 6/10" },
  {
    key: "chiefComplaint",
    label: "Chief complaint",
    placeholder: "e.g. Right anterior knee pain, worse over the last 3 months...",
    multiline: true,
  },
  {
    key: "aggravating",
    label: "Aggravating factors",
    placeholder: "e.g. stairs, squatting, prolonged sitting...",
    multiline: true,
  },
  {
    key: "relieving",
    label: "Relieving factors",
    placeholder: "e.g. rest, ice, stretching...",
    multiline: true,
  },
  {
    key: "previousInjuries",
    label: "Previous injuries",
    placeholder: "e.g. ACL reconstruction (2021), recurring ankle sprains...",
    multiline: true,
  },
];

export function NewPatientForm() {
  const router = useRouter();
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSubmit = form.name.trim().length > 0 && !isSubmitting;

  const setField =
    (key: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setForm((prev) => ({ ...prev, [key]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;

    setIsSubmitting(true);
    setError(null);
    try {
      const payload: PatientCreateInput = { name: form.name.trim() };
      if (form.age.trim()) payload.age = Number(form.age);
      if (form.gender.trim()) payload.gender = form.gender.trim();
      if (form.occupationSport.trim()) payload.occupationSport = form.occupationSport.trim();
      if (form.chiefComplaint.trim()) payload.chiefComplaint = form.chiefComplaint.trim();
      if (form.duration.trim()) payload.duration = form.duration.trim();
      if (form.painScore.trim()) payload.painScore = form.painScore.trim();
      if (form.aggravating.trim()) payload.aggravating = form.aggravating.trim();
      if (form.relieving.trim()) payload.relieving = form.relieving.trim();
      if (form.previousInjuries.trim()) payload.previousInjuries = form.previousInjuries.trim();

      const patient = await api.createPatient(payload);
      const assessment = await api.createAssessment(patient.id);
      router.push(`/assessment/${assessment.id}`);
    } catch {
      setError("Couldn't create the patient. Check the backend is running and try again.");
      setIsSubmitting(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="mx-auto max-w-2xl space-y-5 rounded-2xl border border-slate-200 bg-white p-6"
    >
      <div>
        <h1 className="text-sm font-semibold text-slate-900">New patient intake</h1>
        <p className="mt-1 text-sm text-slate-500">
          Only name is required — everything else can be filled in or updated later.
        </p>
      </div>

      <div>
        <label htmlFor="patient-name" className="text-[11px] font-semibold tracking-wide text-slate-500">
          NAME
        </label>
        <Input
          id="patient-name"
          value={form.name}
          onChange={setField("name")}
          placeholder="e.g. Ankita Sharma"
          autoFocus
          className="mt-2 h-10 rounded-xl border-slate-200 px-3.5 text-sm placeholder:text-slate-400"
        />
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {FIELDS.map((field) => (
          <div key={field.key} className={field.multiline ? "sm:col-span-2" : undefined}>
            <label
              htmlFor={`patient-${field.key}`}
              className="text-[11px] font-semibold tracking-wide text-slate-500"
            >
              {field.label.toUpperCase()}
            </label>
            {field.multiline ? (
              <Textarea
                id={`patient-${field.key}`}
                value={form[field.key]}
                onChange={setField(field.key)}
                placeholder={field.placeholder}
                rows={3}
                className="mt-2 min-h-28 rounded-xl border-slate-200 px-3.5 py-2.5 text-sm placeholder:text-slate-400"
              />
            ) : (
              <Input
                id={`patient-${field.key}`}
                type={field.type ?? "text"}
                value={form[field.key]}
                onChange={setField(field.key)}
                placeholder={field.placeholder}
                className="mt-2 h-10 rounded-xl border-slate-200 px-3.5 text-sm placeholder:text-slate-400"
              />
            )}
          </div>
        ))}
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="flex justify-end">
        <Button
          type="submit"
          disabled={!canSubmit}
          className="rounded-full bg-sky-700 px-5 text-white hover:bg-sky-800"
        >
          {isSubmitting ? "Creating…" : "Start assessment"}
        </Button>
      </div>
    </form>
  );
}
