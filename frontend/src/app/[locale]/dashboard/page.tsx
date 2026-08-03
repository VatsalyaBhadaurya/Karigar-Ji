"use client";

import { useEffect } from "react";
import { useTranslations } from "next-intl";
import Link from "next/link";
import { useAuth } from "@/lib/hooks/useAuth";
import { useProjectStore } from "@/lib/stores/projectStore";
import { listProjects } from "@/lib/api/project";
import { ProjectCard } from "@/components/project/ProjectCard";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Plus } from "lucide-react";
import { Navbar } from "@/components/layout/Navbar";
import { useState } from "react";
import { Project } from "@/lib/types";

export default function DashboardPage() {
  const t = useTranslations("dashboard");
  const { token, loading: authLoading } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    listProjects(token).then((result) => {
      if (result.data) setProjects(result.data);
      setLoading(false);
    });
  }, [token]);

  if (authLoading) return null;

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 py-10">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">{t("title")}</h1>
          <Button asChild className="bg-white text-slate-900 hover:bg-slate-100">
            <Link href="/new-project">
              <Plus className="w-4 h-4 mr-2" />
              {t("newProject")}
            </Link>
          </Button>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => <Skeleton key={i} className="h-48 rounded-xl bg-slate-800" />)}
          </div>
        ) : projects.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-32 text-slate-400">
            <p className="text-xl mb-2">{t("empty")}</p>
            <p className="mb-6">{t("emptyDescription")}</p>
            <Button asChild className="bg-white text-slate-900 hover:bg-slate-100">
              <Link href="/new-project">{t("createFirst")}</Link>
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
