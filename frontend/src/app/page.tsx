import { HeroSection } from "@/components/home/hero-section";
import { QuickActionsBar } from "@/components/home/quick-actions-bar";
import { TopNav } from "@/components/layout/top-nav";

export default function Home() {
  return (
    <div className="flex min-h-full flex-1 flex-col bg-slate-50">
      <TopNav />
      <HeroSection />
      <QuickActionsBar />
    </div>
  );
}
