"use client";

import { useEffect } from "react";
import { useParams } from "next/navigation";
import { useAuth } from "@/lib/hooks/useAuth";
import { getProject } from "@/lib/api/project";
import { useProjectStore } from "@/lib/stores/projectStore";
import { Navbar } from "@/components/layout/Navbar";
import { StepNavigator } from "@/components/workspace/StepNavigator";
import { WorkspacePanel } from "@/components/workspace/WorkspacePanel";
import { Skeleton } from "@/components/ui/skeleton";

export default function ProjectPage() {
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();
  const { project, setProject, activeStep } = useProjectStore();

  useEffect(() => {
    if (!token || !id) return;
    getProject(id, token).then((result) => {
      if (result.data) setProject(result.data);
    });
  }, [token, id]);

  if (!project) {
    return (
      <div className="min-h-screen bg-slate-950 text-white">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 py-10 space-y-4">
          <Skeleton className="h-8 w-64 bg-slate-800" />
          <Skeleton className="h-96 bg-slate-800 rounded-xl" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col">
      <Navbar />
      <div className="flex flex-1 max-w-7xl mx-auto w-full px-4 py-6 gap-6">
        <StepNavigator project={project} />
        <WorkspacePanel project={project} activeStep={activeStep} />
      </div>
    </div>
  );
}
