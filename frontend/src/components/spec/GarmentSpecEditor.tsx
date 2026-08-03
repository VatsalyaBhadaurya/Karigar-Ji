"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/lib/hooks/useAuth";
import { updateSpec } from "@/lib/api/vision";
import { useProjectStore } from "@/lib/stores/projectStore";
import { ProjectFull, GarmentSpec, GarmentSpecRow } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { SpecFieldGroup } from "./SpecFieldGroup";
import { AlertCircle, X, Plus } from "lucide-react";

const PRESET_COLORS = [
  "#000000", "#FFFFFF", "#F5F5DC", "#FFFACD", "#FFC0CB", "#FF69B4",
  "#FF0000", "#8B0000", "#FF7F50", "#FF8C00", "#FFD700", "#ADFF2F",
  "#008000", "#006400", "#00CED1", "#4169E1", "#0000CD", "#8A2BE2",
  "#9400D3", "#800080", "#A0522D", "#808080", "#C0C0C0", "#D4AF37",
];

const UNITS = ["cm", "in"];

export function GarmentSpecEditor({ project }: { project: ProjectFull }) {
  const t = useTranslations("spec");
  const { token } = useAuth();
  const { currentSpec, currentSpecRow, setCurrentSpecRow } = useProjectStore();
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [saveError, setSaveError] = useState("");
  const [newColor, setNewColor] = useState("#FFFFFF");
  const [colorInput, setColorInput] = useState("");

  // Store spec row (set after fresh analysis) takes priority over stale page-load data
  const specRow: GarmentSpecRow | null =
    currentSpecRow ??
    (project.garment_specs?.find((s) => s.is_current) as GarmentSpecRow | undefined) ??
    null;

  const spec: GarmentSpec | null = currentSpec ?? (specRow?.spec_json as GarmentSpec | null ?? null);

  if (!spec) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-3 text-slate-400">
        <AlertCircle className="w-8 h-8" />
        <p>No garment spec yet. Upload a sketch first.</p>
      </div>
    );
  }

  const handleSave = async () => {
    if (!token) { setSaveError("Not authenticated"); return; }
    if (!specRow) { setSaveError("No spec found — analyze a sketch first"); return; }
    setSaving(true);
    setSaveError("");
    const result = await updateSpec(specRow.id, { spec_json: spec }, token);
    if (result.data) {
      setCurrentSpecRow(result.data);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } else {
      setSaveError(result.error?.message ?? "Save failed");
    }
    setSaving(false);
  };

  const update = (field: keyof GarmentSpec, value: unknown) => {
    const updated = { ...spec, [field]: value };
    if (specRow) setCurrentSpecRow({ ...specRow, spec_json: updated });
  };

  const updateMeasurement = (key: string, value: string) => {
    const m = { ...(spec.measurements ?? { unit: "cm" }), [key]: value === "" ? undefined : Number(value) };
    update("measurements", m);
  };

  const addColor = (color: string) => {
    const trimmed = color.trim();
    if (!trimmed || spec.colors.includes(trimmed)) return;
    update("colors", [...spec.colors, trimmed]);
    setColorInput("");
  };

  const removeColor = (color: string) => {
    update("colors", spec.colors.filter((c) => c !== color));
  };

  const measurements = spec.measurements ?? { unit: "cm" };
  const measureFields: Array<{ key: string; label: string }> = [
    { key: "chest", label: "Chest" },
    { key: "waist", label: "Waist" },
    { key: "hip", label: "Hip" },
    { key: "length", label: "Length" },
    { key: "sleeve_length", label: "Sleeve" },
    { key: "shoulder_width", label: "Shoulder" },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
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
        {saveError && <p className="text-red-400 text-xs mt-2 text-right">{saveError}</p>}
      </div>

      {/* Basic fields */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <SpecFieldGroup label={t("garmentType")} value={spec.garment_type} onChange={(v) => update("garment_type", v)} />
        <SpecFieldGroup label={t("silhouette")} value={spec.silhouette} onChange={(v) => update("silhouette", v)} />
        <SpecFieldGroup label={t("neckline")} value={spec.neckline ?? ""} onChange={(v) => update("neckline", v)} />
        <SpecFieldGroup label={t("sleeveType")} value={spec.sleeve_type ?? ""} onChange={(v) => update("sleeve_type", v)} />
        <SpecFieldGroup label={t("fit")} value={spec.fit} onChange={(v) => update("fit", v)} />
        <SpecFieldGroup label="Seam Allowance" value={spec.seam_allowance} onChange={(v) => update("seam_allowance", v)} />
      </div>

      {/* Colors */}
      <div className="space-y-3">
        <Label className="text-slate-400 text-sm">{t("colors")}</Label>

        {/* Current colors */}
        <div className="flex flex-wrap gap-2">
          {spec.colors.map((c) => (
            <span key={c} className="flex items-center gap-1.5 bg-slate-700 rounded-full px-3 py-1 text-sm text-slate-200">
              {c.startsWith("#") && (
                <span className="w-3 h-3 rounded-full border border-slate-500 flex-shrink-0" style={{ background: c }} />
              )}
              {c}
              <button onClick={() => removeColor(c)} className="ml-0.5 text-slate-400 hover:text-white">
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
          {spec.colors.length === 0 && <p className="text-slate-500 text-sm">No colors added yet</p>}
        </div>

        {/* Preset swatches */}
        <div className="flex flex-wrap gap-1.5">
          {PRESET_COLORS.map((hex) => (
            <button
              key={hex}
              onClick={() => addColor(hex)}
              title={hex}
              className="w-6 h-6 rounded-full border-2 border-slate-600 hover:border-white transition-colors flex-shrink-0"
              style={{ background: hex }}
            />
          ))}
        </div>

        {/* Color picker + custom text */}
        <div className="flex gap-2 items-center">
          <input
            type="color"
            value={newColor}
            onChange={(e) => { setNewColor(e.target.value); setColorInput(e.target.value); }}
            className="w-9 h-9 rounded cursor-pointer border border-slate-600 bg-transparent p-0.5 flex-shrink-0"
          />
          <Input
            value={colorInput}
            onChange={(e) => setColorInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addColor(colorInput || newColor)}
            placeholder='Hex (#FF69B4) or name (rose pink)'
            className="flex-1 bg-slate-800 border-slate-700 text-white text-sm h-9"
          />
          <Button
            size="sm"
            variant="outline"
            onClick={() => addColor(colorInput || newColor)}
            className="border-slate-600 text-slate-300 hover:text-white h-9 flex-shrink-0"
          >
            <Plus className="w-3 h-3 mr-1" /> Add
          </Button>
        </div>
      </div>

      {/* Measurements */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <Label className="text-slate-400 text-sm">{t("measurements")}</Label>
          <div className="flex gap-1">
            {UNITS.map((u) => (
              <button
                key={u}
                onClick={() => updateMeasurement("unit", u)}
                className={`px-2 py-0.5 rounded text-xs font-medium transition-colors ${
                  measurements.unit === u
                    ? "bg-white text-slate-900"
                    : "bg-slate-700 text-slate-400 hover:text-white"
                }`}
              >
                {u}
              </button>
            ))}
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {measureFields.map(({ key, label }) => (
            <div key={key} className="space-y-1">
              <Label className="text-slate-500 text-xs">{label} ({measurements.unit})</Label>
              <Input
                type="number"
                min={0}
                step={0.5}
                value={(measurements as Record<string, unknown>)[key] as number ?? ""}
                onChange={(e) => updateMeasurement(key, e.target.value)}
                placeholder="—"
                className="bg-slate-800 border-slate-700 text-white text-sm h-8"
              />
            </div>
          ))}
        </div>
      </div>

      {/* Fabric */}
      <div>
        <Label className="text-slate-400 text-sm">{t("fabric")}</Label>
        <p className="text-slate-200 mt-1">{spec.suggested_fabric.join(", ") || "—"}</p>
      </div>

      {/* Construction notes */}
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
    </div>
  );
}
