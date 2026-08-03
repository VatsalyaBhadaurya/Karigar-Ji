"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface Props {
  label: string;
  value: string;
  onChange: (value: string) => void;
}

export function SpecFieldGroup({ label, value, onChange }: Props) {
  return (
    <div>
      <Label className="text-slate-400 text-xs mb-1 block">{label}</Label>
      <Input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="bg-slate-800 border-slate-700 text-white h-9 text-sm"
      />
    </div>
  );
}
