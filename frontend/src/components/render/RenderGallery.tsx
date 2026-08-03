"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/lib/hooks/useAuth";
import { createRenders, getRender } from "@/lib/api/render";
import { useProjectStore } from "@/lib/stores/projectStore";
import { ProjectFull, Render } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { AIGenerationProgress } from "@/components/workspace/AIGenerationProgress";
import { Download } from "lucide-react";
import { cn } from "@/lib/utils";

const VIEWS = ["front", "back", "side_left", "studio_3q"] as const;

export function RenderGallery({ project }: { project: ProjectFull }) {
  const t = useTranslations("renders");
  const { token } = useAuth();
  const { renders, setRenders, updateRender } = useProjectStore();
  const [generating, setGenerating] = useState(false);
  const [activeView, setActiveView] = useState<string>("front");

  const specRow = project.garment_specs?.find((s) => s.is_current);
  const existingRenders = project.renders ?? [];
  const displayRenders = renders.length > 0 ? renders : existingRenders;

  const startPolling = (renderIds: string[]) => {
    renderIds.forEach((id) => {
      const interval = setInterval(async () => {
        if (!token) return;
        const result = await getRender(id, token);
        if (result.data) {
          updateRender(result.data as Render);
          if (result.data.render_status === "complete" || result.data.render_status === "error") {
            clearInterval(interval);
          }
        } else {
          clearInterval(interval);
        }
      }, 3000);
    });
  };

  const handleGenerate = async () => {
    if (!token || !specRow) return;
    setGenerating(true);
    const result = await createRenders(specRow.id, project.id, token);
    if (result.data) {
      setRenders(result.data.renders as Render[]);
      startPolling(result.data.renders.map((r: Render) => r.id));
    }
    setGenerating(false);
  };

  if (!specRow) {
    return <p className="text-slate-400 py-16 text-center">Complete the garment spec first.</p>;
  }

  const viewLabel: Record<string, string> = {
    front: t("front"), back: t("back"), side_left: t("side"), studio_3q: t("studio"),
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-white">{t("title")}</h2>
        <Button
          onClick={handleGenerate}
          disabled={generating}
          className="bg-white text-slate-900 hover:bg-slate-100 font-semibold"
        >
          {generating ? t("generating") : displayRenders.length > 0 ? "Regenerate" : t("generate")}
        </Button>
      </div>

      {generating && <AIGenerationProgress message={t("generating")} />}

      {displayRenders.length > 0 && (
        <>
          <div className="flex gap-2">
            {VIEWS.map((v) => (
              <button
                key={v}
                onClick={() => setActiveView(v)}
                className={cn(
                  "px-3 py-1.5 rounded-lg text-xs font-medium transition-colors",
                  activeView === v ? "bg-white text-slate-900" : "bg-slate-800 text-slate-400 hover:text-white"
                )}
              >
                {viewLabel[v]}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-2 gap-4">
            {displayRenders.map((render) => (
              <div key={render.id} className="relative bg-slate-800 rounded-xl overflow-hidden aspect-[3/4]">
                {render.render_status === "complete" && render.public_url ? (
                  <>
                    <img src={render.public_url} alt={render.view_type} className="w-full h-full object-cover" />
                    <a
                      href={render.public_url}
                      download
                      className="absolute top-2 right-2 bg-black/60 rounded-lg p-1.5 text-white hover:bg-black/80"
                    >
                      <Download className="w-4 h-4" />
                    </a>
                  </>
                ) : render.render_status === "error" ? (
                  <div className="flex items-center justify-center h-full text-red-400 text-sm">Failed</div>
                ) : (
                  <div className="flex flex-col items-center justify-center h-full gap-2">
                    <Skeleton className="w-full h-full absolute inset-0 bg-slate-700 animate-pulse" />
                    <p className="relative text-slate-400 text-xs z-10">Generating {viewLabel[render.view_type]}...</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </>
      )}

      {displayRenders.length === 0 && !generating && (
        <p className="text-slate-400 text-sm text-center py-8">{t("estimatedTime")}</p>
      )}
    </div>
  );
}
