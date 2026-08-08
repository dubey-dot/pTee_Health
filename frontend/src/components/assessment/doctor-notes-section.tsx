"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Mic, Square } from "lucide-react";

import { api, type DoctorNote } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useVoiceDictation } from "@/lib/use-voice-dictation";

function formatTime(iso: string) {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  // Locale pinned explicitly (not `undefined`) so server and client render
  // the same string — an unpinned locale resolves differently between
  // Node's ICU (SSR) and the browser's, causing a hydration mismatch.
  return date.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export interface DoctorNotesSectionProps {
  assessmentId: string;
  initialNotes?: DoctorNote[];
}

export function DoctorNotesSection({ assessmentId, initialNotes }: DoctorNotesSectionProps) {
  const queryClient = useQueryClient();
  const notesKey = ["notes", assessmentId];

  const { data: notes = [] } = useQuery({
    queryKey: notesKey,
    queryFn: () => api.getNotes(assessmentId),
    initialData: initialNotes,
  });

  const [content, setContent] = useState("");
  const [source, setSource] = useState<"typed" | "voice">("typed");

  const { isListening, voiceError, toggleListening } = useVoiceDictation((transcript) => {
    setSource("voice");
    setContent((prev) => (prev ? `${prev.trim()} ${transcript}` : transcript));
  });

  const createMutation = useMutation({
    mutationFn: (data: { content: string; source: "typed" | "voice" }) =>
      api.createNote(assessmentId, data),
    onSuccess: (note) => {
      queryClient.setQueryData<DoctorNote[]>(notesKey, (prev) => [...(prev ?? []), note]);
      setContent("");
      setSource("typed");
    },
  });

  const canSave = content.trim().length > 0;

  const handleSave = () => {
    if (!canSave) return;
    createMutation.mutate({ content: content.trim(), source });
  };

  return (
    <section>
      <h3 className="text-[11px] font-semibold tracking-wide text-slate-500">
        DOCTOR&apos;S NOTES ({notes.length})
      </h3>

      {notes.length > 0 && (
        <ul className="mt-3 space-y-2">
          {notes.map((note) => (
            <li
              key={note.id}
              className="rounded-xl border border-slate-100 bg-slate-50 px-3.5 py-2.5 text-sm text-slate-700"
            >
              <p className="leading-5">{note.content}</p>
              <p className="mt-1 text-[11px] text-slate-400">
                {formatTime(note.createdAt)}
                {note.source === "voice" ? " · dictated" : ""}
              </p>
            </li>
          ))}
        </ul>
      )}

      <div className="mt-3 flex items-start gap-2 rounded-xl border border-slate-200 py-2 pr-2 pl-3.5 focus-within:border-sky-300 focus-within:ring-3 focus-within:ring-sky-100">
        <textarea
          value={content}
          onChange={(e) => {
            setContent(e.target.value);
            setSource("typed");
          }}
          placeholder='Say “note that…” to dictate a verbatim clinical note, or type here.'
          rows={2}
          className="min-h-[2.5rem] flex-1 resize-none bg-transparent py-1.5 text-sm text-slate-900 placeholder:italic placeholder:text-slate-400 outline-none"
        />
        <button
          type="button"
          onClick={toggleListening}
          aria-pressed={isListening}
          aria-label={isListening ? "Stop dictating note" : "Dictate note by voice"}
          className={cn(
            "mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-white transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400",
            isListening ? "bg-sky-800" : "bg-sky-700 hover:bg-sky-800"
          )}
        >
          {isListening ? <Square className="h-3 w-3" /> : <Mic className="h-3.5 w-3.5" />}
        </button>
      </div>

      {voiceError && (
        <p className="mt-1.5 text-[11px] text-red-600">
          Voice input isn&apos;t supported in this browser — try Chrome or Edge, or type the note
          instead.
        </p>
      )}

      <div className="mt-2 flex justify-end">
        <button
          type="button"
          onClick={handleSave}
          disabled={!canSave || createMutation.isPending}
          className="rounded-full bg-sky-700 px-4 py-1.5 text-sm font-medium text-white transition-colors hover:bg-sky-800 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          {createMutation.isPending ? "Saving…" : "Save note"}
        </button>
      </div>
    </section>
  );
}
