"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import { Project } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-slate-700 text-slate-300",
  analyzing: "bg-blue-900 text-blue-300",
  spec_ready: "bg-amber-900 text-amber-300",
  rendering: "bg-purple-900 text-purple-300",
  render_ready: "bg-indigo-900 text-indigo-300",
  techpack_ready: "bg-emerald-900 text-emerald-300",
  complete: "bg-green-900 text-green-300",
  error: "bg-red-900 text-red-300",
};

export function ProjectCard({ project }: { project: Project }) {
  const t = useTranslations("dashboard");

  return (
    <Link href={`/project/${project.id}`}>
      <Card className="bg-slate-900 border-slate-700 hover:border-slate-500 transition-colors cursor-pointer">
        <CardContent className="p-5">
          {project.thumbnail_url ? (
            <img
              src={project.thumbnail_url}
              alt={project.name}
              className="w-full h-32 object-cover rounded-lg mb-4 bg-slate-800"
            />
          ) : (
            <div className="w-full h-32 rounded-lg mb-4 bg-slate-800 flex items-center justify-center text-slate-600 text-sm">
              No preview yet
            </div>
          )}
          <div className="flex items-start justify-between gap-2">
            <div>
              <h3 className="font-semibold text-white truncate">{project.name}</h3>
              {project.garment_type && (
                <p className="text-slate-400 text-xs mt-0.5">{project.garment_type.replace(/_/g, " ")}</p>
              )}
            </div>
            <Badge className={cn("text-xs shrink-0", STATUS_COLORS[project.status] ?? STATUS_COLORS.draft)}>
              {t(`status.${project.status}` as any)}
            </Badge>
          </div>
          <p className="text-slate-500 text-xs mt-3">
            {t("lastUpdated")} {new Date(project.updated_at).toLocaleDateString()}
          </p>
        </CardContent>
      </Card>
    </Link>
  );
}
