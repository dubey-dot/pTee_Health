"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Mic, Sparkles, Trophy } from "lucide-react";

const HERO_VARIANTS = [
  {
    highlight: "decisions",
    badgeIcon: Sparkles,
    badgeText: "12+ years of PTee Health know-how",
  },
  {
    highlight: "tracking",
    badgeIcon: Trophy,
    badgeText: "50,000+ sessions reasoned through",
  },
] as const;

const ROTATE_INTERVAL_MS = 4000;

export function HeroSection() {
  const [variantIndex, setVariantIndex] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setVariantIndex((i) => (i + 1) % HERO_VARIANTS.length);
    }, ROTATE_INTERVAL_MS);
    return () => clearInterval(id);
  }, []);

  const variant = HERO_VARIANTS[variantIndex];
  const BadgeIcon = variant.badgeIcon;

  return (
    <main className="flex flex-1 flex-col items-center justify-center px-6 py-16 text-center">
      <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl md:text-6xl">
        Treatment{" "}
        <span
          key={variant.highlight}
          className="inline-block text-sky-600 transition-opacity duration-500"
        >
          {variant.highlight}
        </span>
        <br />
        made smarter.
      </h1>

      <p className="mt-4 max-w-xl text-base text-slate-500 sm:text-lg">
        AI Assistant for Physiotherapists, built from years of PTee Health&apos;s
        expertise.
      </p>

      <div
        key={variant.badgeText}
        className="mt-8 flex items-center gap-2 rounded-full border border-sky-100 bg-white px-4 py-2 shadow-sm transition-opacity duration-500"
      >
        <span className="flex h-5 w-5 items-center justify-center rounded-full bg-sky-600 text-white">
          <Sparkles className="h-3 w-3" />
        </span>
        <BadgeIcon className="h-4 w-4 text-sky-500" />
        <span className="text-sm font-medium text-slate-700">
          {variant.badgeText}
        </span>
      </div>

      <Link
        href="/assessment"
        aria-label="Start new assessment"
        className="group relative mt-10 flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-sky-500 to-sky-700 shadow-lg shadow-sky-300/50 transition-transform hover:scale-105 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-sky-300 sm:h-24 sm:w-24"
      >
        <span className="absolute inset-0 -z-10 rounded-full bg-sky-400/40 blur-xl transition-opacity group-hover:opacity-70" />
        <Mic className="h-8 w-8 text-white sm:h-9 sm:w-9" />
      </Link>

      <p className="mt-6 max-w-md text-sm text-slate-500 sm:text-base">
        <span className="font-semibold text-slate-900">Start here:</span> Tap to
        begin new assessment and speak naturally while AI listens and tracks
        all the information.
      </p>
    </main>
  );
}
