"use client";

import { ProjectFull } from "@/lib/types";
import { SketchUploader } from "@/components/upload/SketchUploader";
import { GarmentSpecEditor } from "@/components/spec/GarmentSpecEditor";
import { RenderGallery } from "@/components/render/RenderGallery";
import { TechPackViewer } from "@/components/techpack/TechPackViewer";
import { PatternSVGViewer } from "@/components/pattern/PatternSVGViewer";
import { ExportPanel } from "@/components/export/ExportPanel";

interface Props {
  project: ProjectFull;
  activeStep: string;
}

export function WorkspacePanel({ project, activeStep }: Props) {
  return (
    <main className="flex-1 min-w-0">
      <div className="bg-slate-900 rounded-xl border border-slate-800 min-h-[600px] p-6">
        {activeStep === "upload" && <SketchUploader project={project} />}
        {activeStep === "spec" && <GarmentSpecEditor project={project} />}
        {activeStep === "renders" && <RenderGallery project={project} />}
        {activeStep === "techpack" && <TechPackViewer project={project} />}
        {activeStep === "pattern" && <PatternSVGViewer project={project} />}
        {activeStep === "export" && <ExportPanel project={project} />}
      </div>
    </main>
  );
}
