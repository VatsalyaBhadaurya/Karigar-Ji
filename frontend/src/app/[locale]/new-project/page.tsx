"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/lib/hooks/useAuth";
import { createProject } from "@/lib/api/project";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Navbar } from "@/components/layout/Navbar";

export default function NewProjectPage() {
  const t = useTranslations("project");
  const router = useRouter();
  const { token } = useAuth();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCreate = async () => {
    if (!token || !name.trim()) return;
    setLoading(true);
    const result = await createProject(name.trim(), description.trim(), token);
    if (result.error) {
      setError(result.error.message);
      setLoading(false);
      return;
    }
    router.push(`/project/${result.data!.id}`);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <Navbar />
      <main className="max-w-xl mx-auto px-4 py-16">
        <h1 className="text-3xl font-bold mb-8">{t("create")}</h1>
        <div className="space-y-6">
          <div>
            <Label className="text-slate-300 mb-2 block">{t("name")}</Label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Summer Anarkali Collection"
              className="bg-slate-800 border-slate-700 text-white"
            />
          </div>
          <div>
            <Label className="text-slate-300 mb-2 block">{t("description")}</Label>
            <Textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief description (optional)"
              className="bg-slate-800 border-slate-700 text-white"
              rows={3}
            />
          </div>
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <Button
            onClick={handleCreate}
            disabled={loading || !name.trim()}
            className="w-full bg-white text-slate-900 hover:bg-slate-100 font-semibold"
          >
            {loading ? "Creating..." : t("create")}
          </Button>
        </div>
      </main>
    </div>
  );
}
