"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/lib/hooks/useAuth";
import { apiRequest } from "@/lib/api/client";
import { ProjectFull } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { AIGenerationProgress } from "@/components/workspace/AIGenerationProgress";
import { WhatsAppShare } from "./WhatsAppShare";
import { Download } from "lucide-react";

const ARTIFACT_OPTIONS = [
  { key: "renders", labelKey: "renders" },
  { key: "techpack", labelKey: "techpack" },
  { key: "patterns", labelKey: "patterns" },
  { key: "flats", labelKey: "flats" },
] as const;

export function ExportPanel({ project }: { project: ProjectFull }) {
  const t = useTranslations("export");
  const { token } = useAuth();
  const [selected, setSelected] = useState<Record<string, boolean>>({ renders: true, techpack: true });
  const [generating, setGenerating] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState("");

  const handleExport = async () => {
    if (!token) return;
    setGenerating(true);
    const include = Object.entries(selected).filter(([, v]) => v).map(([k]) => k);
    const result = await apiRequest<{ signed_url: string }>("/export", {
      method: "POST",
      body: { project_id: project.id, export_type: "zip", include },
      token,
    });
    if (result.data?.signed_url) setDownloadUrl(result.data.signed_url);
    setGenerating(false);
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-white">{t("title")}</h2>

      <div className="bg-slate-800 rounded-xl p-5 space-y-4">
        <p className="text-slate-300 text-sm font-medium">{t("selectArtifacts")}</p>
        {ARTIFACT_OPTIONS.map(({ key, labelKey }) => (
          <div key={key} className="flex items-center justify-between">
            <Label className="text-slate-300">{t(labelKey)}</Label>
            <Switch
              checked={selected[key] ?? false}
              onCheckedChange={(v) => setSelected((s) => ({ ...s, [key]: v }))}
            />
          </div>
        ))}
      </div>

      {generating && <AIGenerationProgress message="Bundling your artifacts..." />}

      <div className="flex gap-3">
        <Button
          onClick={handleExport}
          disabled={generating}
          className="bg-white text-slate-900 hover:bg-slate-100 font-semibold"
        >
          <Download className="w-4 h-4 mr-2" />
          {t("downloadZip")}
        </Button>
        {downloadUrl && (
          <Button asChild variant="outline" className="border-slate-600 text-white hover:bg-slate-800">
            <a href={downloadUrl} download>Re-download ZIP</a>
          </Button>
        )}
      </div>

      <WhatsAppShare project={project} shareUrl={downloadUrl} />
    </div>
  );
}
