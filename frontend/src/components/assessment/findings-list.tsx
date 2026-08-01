"use client";

import { useState } from "react";
import { Plus } from "lucide-react";

import { FindingRow, type Finding } from "@/components/assessment/finding-row";
import { InsightsPanel } from "@/components/assessment/insights-panel";
import { LogTestPanel } from "@/components/assessment/log-test-panel";

const INITIAL_FINDINGS: Finding[] = [
  {
    id: "pelvis-shift",
    tag: "GAIT",
    label: "Pelvis Shift Right/Left",
    selected: true,
    detail: {
      question: "Is the pelvis shifted to one side over the feet?",
      bullets: [
        "Shift right / left",
        "Weight distribution",
        "Lateral trunk lean",
        "Frontal-plane symmetry",
      ],
    },
  },
  { id: "pelvis-rotation", tag: "JOINT", label: "Pelvis Rotation Right/Left" },
  { id: "ribcage-position", tag: "JOINT", label: "Ribcage Position" },
  { id: "neck-position", tag: "JOINT", label: "Neck Position" },
  { id: "spinal-position", tag: "JOINT", label: "Spinal Position" },
];

export function FindingsList() {
  const [findings, setFindings] = useState<Finding[]>(INITIAL_FINDINGS);
  const [showLogTest, setShowLogTest] = useState(false);

  const handleDelete = (id: string) => {
    setFindings((prev) => prev.filter((f) => f.id !== id));
  };

  const handleRelabel = (id: string, newLabel: string) => {
    setFindings((prev) =>
      prev.map((f) => (f.id === id ? { ...f, label: newLabel } : f))
    );
  };

  return (
    <div className="space-y-2">
      {findings.map((finding) => (
        <FindingRow
          key={finding.id}
          finding={finding}
          onDelete={handleDelete}
          onRelabel={handleRelabel}
        />
      ))}

      {showLogTest ? (
        <LogTestPanel onClose={() => setShowLogTest(false)} onSave={() => setShowLogTest(false)} />
      ) : (
        <button
          type="button"
          onClick={() => setShowLogTest(true)}
          className="flex w-full items-center justify-center gap-1.5 rounded-xl border border-dashed border-sky-200 py-3 text-sm font-medium text-sky-700 transition-colors hover:bg-sky-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400"
        >
          <Plus className="h-3.5 w-3.5" />
          Log a test
        </button>
      )}

      <InsightsPanel />
    </div>
  );
}
