import { Crop, MessageSquare, Pencil, Type } from "lucide-react";

const ACTIONS = [
  { label: "Crop image", icon: Crop },
  { label: "Type finding", icon: Type },
  { label: "Draw / annotate", icon: Pencil },
  { label: "Ask PTee Assistant", icon: MessageSquare },
] as const;

export function QuickActionsBar() {
  return (
    <div className="fixed bottom-6 left-1/2 flex -translate-x-1/2 items-center gap-1 rounded-full border border-slate-200 bg-white p-1.5 shadow-lg">
      {ACTIONS.map((action) => (
        <button
          key={action.label}
          type="button"
          aria-label={action.label}
          className="flex h-9 w-9 items-center justify-center rounded-full text-slate-500 transition-colors hover:bg-slate-50 hover:text-slate-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400"
        >
          <action.icon className="h-4 w-4" />
        </button>
      ))}
    </div>
  );
}
