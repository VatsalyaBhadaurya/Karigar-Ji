"use client";

import { useTranslations } from "next-intl";
import { ProjectFull } from "@/lib/types";
import { Scissors } from "lucide-react";

export function PatternSVGViewer({ project }: { project: ProjectFull }) {
  const t = useTranslations("pattern");

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-white">{t("title")}</h2>
      </div>
      <div className="flex flex-col items-center justify-center py-20 gap-3 text-slate-500">
        <Scissors className="w-10 h-10" />
        <p className="text-center">Pattern Engine — Phase 5</p>
        <p className="text-sm text-center">Deterministic geometry engine coming in the next build phase.</p>
      </div>
    </div>
  );
}
