"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/lib/hooks/useAuth";
import { apiRequest } from "@/lib/api/client";
import { ProjectFull } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { AIGenerationProgress } from "@/components/workspace/AIGenerationProgress";
import { Download, Package } from "lucide-react";

export function TechPackViewer({ project }: { project: ProjectFull }) {
  const t = useTranslations("techpack");
  const { token } = useAuth();
  const [generating, setGenerating] = useState(false);
  const [pdfUrl, setPdfUrl] = useState(project.techpacks?.[0]?.pdf_url ?? "");

  const specRow = project.garment_specs?.find((s) => s.is_current);

  const handleGenerate = async () => {
    if (!token || !specRow) return;
    setGenerating(true);
    const result = await apiRequest<{ pdf_url: string }>("/techpack", {
      method: "POST",
      body: { spec_id: specRow.id, project_id: project.id },
      token,
    });
    if (result.data?.pdf_url) setPdfUrl(result.data.pdf_url);
    setGenerating(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-white">{t("title")}</h2>
        <div className="flex gap-2">
          {pdfUrl && (
            <Button asChild variant="outline" size="sm" className="border-slate-600 text-white hover:bg-slate-800">
              <a href={pdfUrl} download>
                <Download className="w-4 h-4 mr-1" />
                {t("download")}
              </a>
            </Button>
          )}
          <Button
            onClick={handleGenerate}
            disabled={generating || !specRow}
            size="sm"
            className="bg-white text-slate-900 hover:bg-slate-100"
          >
            {generating ? "Generating..." : pdfUrl ? "Regenerate" : t("generate")}
          </Button>
        </div>
      </div>

      {generating && <AIGenerationProgress message="Generating professional tech pack..." />}

      {pdfUrl && !generating && (
        <iframe
          src={`${pdfUrl}#toolbar=0`}
          className="w-full h-[600px] rounded-xl border border-slate-700"
          title="Tech Pack PDF"
        />
      )}

      {!pdfUrl && !generating && (
        <div className="flex flex-col items-center justify-center py-20 gap-3 text-slate-500">
          <Package className="w-10 h-10" />
          <p>Generate a professional tech pack from your garment spec.</p>
        </div>
      )}
    </div>
  );
}
