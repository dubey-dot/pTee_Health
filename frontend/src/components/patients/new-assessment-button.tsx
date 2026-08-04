"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

export function NewAssessmentButton({ patientId }: { patientId: string }) {
  const router = useRouter();
  const [isCreating, setIsCreating] = useState(false);

  const handleClick = async () => {
    setIsCreating(true);
    const assessment = await api.createAssessment(patientId);
    router.push(`/assessment/${assessment.id}`);
  };

  return (
    <Button
      type="button"
      onClick={handleClick}
      disabled={isCreating}
      className="rounded-full bg-sky-700 px-4 text-white hover:bg-sky-800"
    >
      {isCreating ? "Starting…" : "+ New assessment"}
    </Button>
  );
}
