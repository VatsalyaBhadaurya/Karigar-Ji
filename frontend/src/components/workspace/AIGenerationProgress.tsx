"use client";

import { Progress } from "@/components/ui/progress";
import { Loader2 } from "lucide-react";

interface Props {
  message: string;
  progress?: number;
}

export function AIGenerationProgress({ message, progress }: Props) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-4">
      <Loader2 className="w-8 h-8 text-white animate-spin" />
      <p className="text-slate-300">{message}</p>
      {progress !== undefined && (
        <div className="w-64">
          <Progress value={progress} className="h-1.5 bg-slate-700" />
        </div>
      )}
    </div>
  );
}
