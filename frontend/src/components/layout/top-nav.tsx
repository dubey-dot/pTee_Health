import { Bell, Search, Sparkles } from "lucide-react";

const NAV_ITEMS = [
  { label: "New Patients", href: "/" },
  { label: "Existing Patients", href: "#" },
  { label: "Dashboard", href: "#" },
] as const;

export interface TopNavProps {
  active?: (typeof NAV_ITEMS)[number]["label"];
}

export function TopNav({ active = "New Patients" }: TopNavProps) {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-sky-700 text-xs font-semibold text-white">
              P
            </span>
            <span className="text-sm font-semibold text-slate-900">
              PTee Health
            </span>
          </div>

          <nav className="flex items-center gap-1">
            {NAV_ITEMS.map((item) =>
              item.label === active ? (
                <span
                  key={item.label}
                  className="rounded-full bg-sky-700 px-4 py-1.5 text-sm font-medium text-white"
                >
                  {item.label}
                </span>
              ) : (
                <a
                  key={item.label}
                  href={item.href}
                  className="rounded-full px-4 py-1.5 text-sm font-medium text-slate-500 transition-colors hover:text-slate-700"
                >
                  {item.label}
                </a>
              )
            )}
          </nav>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex h-9 w-56 items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 text-slate-400">
            <Search className="h-4 w-4 shrink-0" />
            <span className="flex-1 text-sm">Search...</span>
            <kbd className="rounded border border-slate-200 bg-white px-1.5 py-0.5 text-[10px] font-medium text-slate-400">
              ⌘K
            </kbd>
          </div>

          <button
            type="button"
            aria-label="Notifications"
            className="relative flex h-9 w-9 items-center justify-center rounded-full text-slate-500 transition-colors hover:bg-slate-50 hover:text-slate-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400"
          >
            <Bell className="h-4.5 w-4.5" />
            <span className="absolute top-2 right-2.5 h-1.5 w-1.5 rounded-full bg-red-500" />
          </button>

          <button
            type="button"
            aria-label="AI assistant"
            className="flex h-9 w-9 items-center justify-center rounded-full text-sky-600 transition-colors hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400"
          >
            <Sparkles className="h-4.5 w-4.5" />
          </button>

          <span className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-900 text-xs font-semibold text-white">
            AR
          </span>
        </div>
      </div>
    </header>
  );
}
