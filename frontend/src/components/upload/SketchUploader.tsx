"use client";

import { useRef, useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/lib/hooks/useAuth";
import { uploadSketch } from "@/lib/api/upload";
import { analyzeSketch } from "@/lib/api/vision";
import { getProject } from "@/lib/api/project";
import { useProjectStore } from "@/lib/stores/projectStore";
import { ProjectFull } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { AIGenerationProgress } from "@/components/workspace/AIGenerationProgress";
import { Upload, CheckCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export function SketchUploader({ project }: { project: ProjectFull }) {
  const t = useTranslations("project");
  const { token } = useAuth();
  const { setCurrentSpecRow, setProject, setActiveStep } = useProjectStore();
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [status, setStatus] = useState<"idle" | "uploading" | "analyzing" | "done" | "error">("idle");
  const [error, setError] = useState("");

  const existingUpload = project.uploads?.[0];

  const handleFile = async (file: File) => {
    if (!token) return;
    setStatus("uploading");
    setError("");

    const uploadResult = await uploadSketch(file, project.id, token);
    if (uploadResult.error) {
      setError(uploadResult.error.message);
      setStatus("error");
      return;
    }

    setStatus("analyzing");
    const specResult = await analyzeSketch(uploadResult.data!.id, project.id, token);
    if (specResult.error) {
      setError(specResult.error.message);
      setStatus("error");
      return;
    }

    setCurrentSpecRow(specResult.data!);
    // Refresh project so garment_specs is current (enables save after page navigation)
    getProject(project.id, token).then((r) => { if (r.data) setProject(r.data); });
    setStatus("done");
    setTimeout(() => setActiveStep("spec"), 1500);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  if (status === "uploading") return <AIGenerationProgress message="Uploading sketch..." progress={30} />;
  if (status === "analyzing") return <AIGenerationProgress message={t("analyzing")} progress={65} />;

  if (status === "done") {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-4 text-green-400">
        <CheckCircle className="w-10 h-10" />
        <p className="text-lg font-medium">Analysis complete! Moving to Spec...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <h2 className="text-xl font-semibold text-white">{t("upload")}</h2>
      {existingUpload && (
        <div className="bg-slate-800 rounded-lg p-4 flex items-center gap-4">
          <img src={existingUpload.public_url} alt="Uploaded sketch" className="w-20 h-20 object-contain rounded" />
          <div>
            <p className="text-white text-sm font-medium">{existingUpload.file_name}</p>
            <p className="text-slate-400 text-xs">Previously uploaded</p>
          </div>
        </div>
      )}
      <div
        onDrop={onDrop}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onClick={() => inputRef.current?.click()}
        className={cn(
          "border-2 border-dashed rounded-xl p-16 flex flex-col items-center justify-center gap-4 cursor-pointer transition-colors",
          isDragging ? "border-white bg-slate-800" : "border-slate-700 hover:border-slate-500 hover:bg-slate-800/50"
        )}
      >
        <Upload className="w-10 h-10 text-slate-500" />
        <p className="text-slate-300 text-center">{t("uploadHint")}</p>
        <Button variant="outline" className="border-slate-600 text-white hover:bg-slate-700" onClick={(e) => { e.stopPropagation(); inputRef.current?.click(); }}>
          Choose File
        </Button>
        <input
          ref={inputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp,application/pdf"
          className="hidden"
          onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }}
        />
      </div>
      {error && <p className="text-red-400 text-sm">{error}</p>}
    </div>
  );
}
