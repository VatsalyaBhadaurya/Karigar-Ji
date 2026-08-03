"use client";

import { useTranslations } from "next-intl";
import { useProjectStore } from "@/lib/stores/projectStore";
import { ProjectFull } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Upload, FileText, Image, Package, Scissors, Download } from "lucide-react";

const STEPS = [
  { key: "upload", icon: Upload },
  { key: "spec", icon: FileText },
  { key: "renders", icon: Image },
  { key: "techpack", icon: Package },
  { key: "pattern", icon: Scissors },
  { key: "export", icon: Download },
] as const;

export function StepNavigator({ project }: { project: ProjectFull }) {
  const t = useTranslations("project.steps");
  const { activeStep, setActiveStep } = useProjectStore();

  return (
    <aside className="w-52 shrink-0">
      <div className="bg-slate-900 rounded-xl border border-slate-800 p-3">
        <p className="text-xs text-slate-500 font-medium uppercase tracking-wider px-2 mb-3">Workflow</p>
        <nav className="space-y-1">
          {STEPS.map(({ key, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setActiveStep(key)}
              className={cn(
                "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors text-left",
                activeStep === key
                  ? "bg-white text-slate-900 font-medium"
                  : "text-slate-400 hover:text-white hover:bg-slate-800"
              )}
            >
              <Icon className="w-4 h-4 shrink-0" />
              {t(key)}
            </button>
          ))}
        </nav>
      </div>
    </aside>
  );
}
