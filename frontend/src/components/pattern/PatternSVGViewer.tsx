"use client";

import { useState } from "react";
import { useAuth } from "@/lib/hooks/useAuth";
import { apiRequest } from "@/lib/api/client";
import { useProjectStore } from "@/lib/stores/projectStore";
import { ProjectFull } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { AIGenerationProgress } from "@/components/workspace/AIGenerationProgress";
import { Download, Scissors, ZoomIn, ZoomOut } from "lucide-react";

interface PatternResult {
  id: string;
  svg_url: string;
  pieces: string[];
  piece_count: number;
}

export function PatternSVGViewer({ project }: { project: ProjectFull }) {
  const { token } = useAuth();
  const { currentSpecRow } = useProjectStore();
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<PatternResult | null>(null);
  const [zoom, setZoom] = useState(1);
  const [error, setError] = useState("");

  const specRow =
    currentSpecRow ??
    (project.garment_specs?.find((s) => s.is_current) as typeof currentSpecRow);

  const existingPattern = project.patterns?.[0];
  const svgUrl = result?.svg_url ?? (existingPattern?.pattern_status === "complete" ? (existingPattern as any).svg_url : null);

  const handleGenerate = async () => {
    if (!token || !specRow) return;
    setGenerating(true);
    setError("");
    const res = await apiRequest<PatternResult>("/pattern", {
      method: "POST",
      body: { spec_id: specRow.id, project_id: project.id },
      token,
    });
    if (res.data) {
      setResult(res.data);
    } else {
      setError(res.error?.message ?? "Pattern generation failed");
    }
    setGenerating(false);
  };

  const pieces = result?.pieces ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-white">Pattern Engine</h2>
        <div className="flex gap-2 items-center">
          {svgUrl && (
            <>
              <button onClick={() => setZoom((z) => Math.max(0.3, z - 0.2))} className="p-1.5 rounded bg-slate-800 text-slate-400 hover:text-white">
                <ZoomOut className="w-4 h-4" />
              </button>
              <span className="text-slate-400 text-xs w-10 text-center">{Math.round(zoom * 100)}%</span>
              <button onClick={() => setZoom((z) => Math.min(3, z + 0.2))} className="p-1.5 rounded bg-slate-800 text-slate-400 hover:text-white">
                <ZoomIn className="w-4 h-4" />
              </button>
              <a href={svgUrl} download className="p-1.5 rounded bg-slate-800 text-slate-400 hover:text-white">
                <Download className="w-4 h-4" />
              </a>
            </>
          )}
          <Button
            onClick={handleGenerate}
            disabled={generating || !specRow}
            size="sm"
            className="bg-white text-slate-900 hover:bg-slate-100"
          >
            {generating ? "Generating…" : svgUrl ? "Regenerate" : "Generate Pattern"}
          </Button>
        </div>
      </div>

      {generating && <AIGenerationProgress message="Drafting pattern blocks…" />}
      {error && <p className="text-red-400 text-sm">{error}</p>}

      {pieces.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {pieces.map((p) => (
            <span key={p} className="bg-slate-800 text-slate-300 text-xs px-2 py-1 rounded-full">
              {p.replace(/_/g, " ")}
            </span>
          ))}
        </div>
      )}

      {svgUrl && !generating ? (
        <div className="overflow-auto rounded-xl border border-slate-700 bg-slate-900 p-4" style={{ maxHeight: 600 }}>
          <div style={{ transform: `scale(${zoom})`, transformOrigin: "top left", transition: "transform 0.2s" }}>
            <img src={svgUrl} alt="Pattern pieces" className="max-w-none" />
          </div>
        </div>
      ) : !generating && !svgUrl ? (
        <div className="flex flex-col items-center justify-center py-20 gap-3 text-slate-500">
          <Scissors className="w-10 h-10" />
          <p className="text-center">Deterministic geometry engine — no AI, pure math.</p>
          <p className="text-sm text-slate-600 text-center">Generates bodice, skirt, and sleeve blocks from your spec measurements.</p>
        </div>
      ) : null}
    </div>
  );
}
