"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/lib/hooks/useAuth";
import { updateSpec } from "@/lib/api/vision";
import { useProjectStore } from "@/lib/stores/projectStore";
import { ProjectFull, GarmentSpec } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { SpecFieldGroup } from "./SpecFieldGroup";
import { AlertCircle } from "lucide-react";

export function GarmentSpecEditor({ project }: { project: ProjectFull }) {
  const t = useTranslations("spec");
  const { token } = useAuth();
  const { currentSpec, setCurrentSpec } = useProjectStore();
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const specRow = project.garment_specs?.find((s) => s.is_current);
  const spec: GarmentSpec | null = currentSpec ?? (specRow?.spec_json as unknown as GarmentSpec ?? null);

  if (!spec) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-3 text-slate-400">
        <AlertCircle className="w-8 h-8" />
        <p>No garment spec yet. Upload a sketch first.</p>
      </div>
    );
  }

  const handleSave = async () => {
    if (!token || !specRow) return;
    setSaving(true);
    const result = await updateSpec(specRow.id, { spec_json: spec }, token);
    if (result.data) {
      setCurrentSpec(result.data.spec_json as GarmentSpec);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    }
    setSaving(false);
  };

  const update = (field: keyof GarmentSpec, value: unknown) => {
    setCurrentSpec({ ...spec, [field]: value });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-white">{t("title")}</h2>
        <div className="flex items-center gap-3">
          {spec.metadata?.confidence !== undefined && (
            <Badge className="bg-slate-700 text-slate-300 text-xs">
              {t("confidence")}: {Math.round(spec.metadata.confidence * 100)}%
            </Badge>
          )}
          <Button onClick={handleSave} disabled={saving} size="sm" className="bg-white text-slate-900 hover:bg-slate-100">
            {saved ? "Saved!" : saving ? "Saving..." : t("saveSpec")}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <SpecFieldGroup label={t("garmentType")} value={spec.garment_type} onChange={(v) => update("garment_type", v)} />
        <SpecFieldGroup label={t("silhouette")} value={spec.silhouette} onChange={(v) => update("silhouette", v)} />
        <SpecFieldGroup label={t("neckline")} value={spec.neckline ?? ""} onChange={(v) => update("neckline", v)} />
        <SpecFieldGroup label={t("sleeveType")} value={spec.sleeve_type ?? ""} onChange={(v) => update("sleeve_type", v)} />
        <SpecFieldGroup label={t("fit")} value={spec.fit} onChange={(v) => update("fit", v)} />
        <SpecFieldGroup label="Seam Allowance" value={spec.seam_allowance} onChange={(v) => update("seam_allowance", v)} />
      </div>

      <div>
        <Label className="text-slate-400 text-sm">{t("fabric")}</Label>
        <p className="text-slate-200 mt-1">{spec.suggested_fabric.join(", ") || "—"}</p>
      </div>

      <div>
        <Label className="text-slate-400 text-sm">{t("colors")}</Label>
        <div className="flex flex-wrap gap-2 mt-1">
          {spec.colors.map((c) => <Badge key={c} className="bg-slate-700 text-slate-200">{c}</Badge>)}
        </div>
      </div>

      {spec.construction_notes.length > 0 && (
        <div>
          <Label className="text-slate-400 text-sm">{t("constructionNotes")}</Label>
          <ul className="mt-1 space-y-1">
            {spec.construction_notes.map((note, i) => (
              <li key={i} className="text-slate-300 text-sm">• {note}</li>
            ))}
          </ul>
        </div>
      )}

      {spec.measurements && (
        <div>
          <Label className="text-slate-400 text-sm">{t("measurements")}</Label>
          <div className="grid grid-cols-3 gap-2 mt-2">
            {Object.entries(spec.measurements)
              .filter(([k]) => k !== "unit")
              .map(([k, v]) => (
                <div key={k} className="bg-slate-800 rounded-lg p-2 text-center">
                  <p className="text-slate-400 text-xs capitalize">{k.replace(/_/g, " ")}</p>
                  <p className="text-white font-mono">{v ?? "—"} {spec.measurements!.unit}</p>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
