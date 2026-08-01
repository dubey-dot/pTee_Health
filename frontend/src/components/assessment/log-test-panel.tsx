"use client";

import { useState } from "react";
import { Check, Mic, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

const TEST_TYPES = [
  { value: "joint", label: "Joint" },
  { value: "muscle", label: "Muscle" },
  { value: "gait", label: "Gait" },
] as const;

type TestType = (typeof TEST_TYPES)[number]["value"];

export interface LoggedTest {
  type: TestType;
  name: string;
  result: string;
}

export interface LogTestPanelProps {
  onClose?: () => void;
  onSave?: (test: LoggedTest) => void;
}

export function LogTestPanel({ onClose, onSave }: LogTestPanelProps) {
  const [testType, setTestType] = useState<TestType>("joint");
  const [testName, setTestName] = useState("");
  const [result, setResult] = useState("");
  const [isListening, setIsListening] = useState(false);

  const canSave = testName.trim().length > 0;

  const handleSave = () => {
    if (!canSave) return;
    onSave?.({ type: testType, name: testName.trim(), result: result.trim() });
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-900">Log a test</h3>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close log a test panel"
          className="rounded-md p-0.5 text-slate-400 transition-colors hover:text-slate-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="mt-4">
        <span className="text-[11px] font-semibold tracking-wide text-slate-500">
          TYPE OF TEST
        </span>
        <div className="mt-2 flex gap-2">
          {TEST_TYPES.map((t) => (
            <button
              key={t.value}
              type="button"
              aria-pressed={testType === t.value}
              onClick={() => setTestType(t.value)}
              className={cn(
                "rounded-full border px-4 py-1.5 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400",
                testType === t.value
                  ? "border-sky-200 bg-sky-50 text-sky-700"
                  : "border-slate-200 bg-white text-slate-600 hover:bg-slate-50"
              )}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-4">
        <label
          htmlFor="log-test-name"
          className="text-[11px] font-semibold tracking-wide text-slate-500"
        >
          TEST NAME
        </label>
        <Input
          id="log-test-name"
          value={testName}
          onChange={(e) => setTestName(e.target.value)}
          placeholder="e.g. Single leg bridge"
          className="mt-2 h-10 rounded-xl border-slate-200 px-3.5 text-sm placeholder:text-slate-400"
        />
      </div>

      <div className="mt-4">
        <label
          htmlFor="log-test-result"
          className="text-[11px] font-semibold tracking-wide text-slate-500"
        >
          RESULT <span className="font-normal text-slate-400">(optional)</span>
        </label>
        <div className="mt-2 flex items-center gap-2 rounded-xl border border-slate-200 py-1 pr-1.5 pl-3.5 focus-within:border-sky-300 focus-within:ring-3 focus-within:ring-sky-100">
          <input
            id="log-test-result"
            value={result}
            onChange={(e) => setResult(e.target.value)}
            placeholder="What did you find?"
            className="h-8 flex-1 min-w-0 bg-transparent text-sm text-slate-900 placeholder:text-slate-400 outline-none"
          />
          <button
            type="button"
            onClick={() => setIsListening((v) => !v)}
            aria-pressed={isListening}
            aria-label="Record result by voice"
            className={cn(
              "flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-white transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400",
              isListening ? "bg-sky-800" : "bg-sky-700 hover:bg-sky-800"
            )}
          >
            <Mic className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      <div className="mt-4 flex justify-end">
        <Button
          type="button"
          onClick={handleSave}
          disabled={!canSave}
          className="rounded-full bg-sky-700 px-4 text-white hover:bg-sky-800"
        >
          <Check className="h-3.5 w-3.5" />
          Save test
        </Button>
      </div>
    </div>
  );
}
