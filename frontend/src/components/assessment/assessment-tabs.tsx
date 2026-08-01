import { UserRound } from "lucide-react";

const TABS = ["Assessment", "Treatment", "Home Plan", "Evaluation"] as const;

export function AssessmentTabs() {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-6 border-b border-slate-200">
        {TABS.map((tab) =>
          tab === "Assessment" ? (
            <span
              key={tab}
              className="rounded-full bg-sky-700 px-4 py-1.5 text-sm font-medium text-white"
            >
              {tab}
            </span>
          ) : tab === "Evaluation" ? (
            <span
              key={tab}
              className="border-b-2 border-sky-600 pb-3 text-sm font-medium text-sky-700"
            >
              {tab}
            </span>
          ) : (
            <span key={tab} className="pb-3 text-sm font-medium text-slate-400">
              {tab}
            </span>
          )
        )}
      </div>

      <span className="flex items-center gap-1.5 rounded-full border border-sky-200 bg-sky-50 px-3 py-1.5 text-xs font-medium text-sky-700">
        <UserRound className="h-3.5 w-3.5" />
        Senior review
      </span>
    </div>
  );
}
