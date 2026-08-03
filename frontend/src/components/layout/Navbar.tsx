"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { LocaleSwitcher } from "./LocaleSwitcher";
import { LayoutDashboard, Plus, LogOut } from "lucide-react";

export function Navbar() {
  const t = useTranslations("nav");
  const { signOut } = useAuth();
  const router = useRouter();

  const handleSignOut = async () => {
    await signOut();
    router.push("/auth/login");
  };

  return (
    <nav className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link href="/dashboard" className="font-bold text-lg text-white tracking-tight">
          KarigarJi
        </Link>
        <div className="flex items-center gap-2">
          <Button asChild variant="ghost" size="sm" className="text-slate-400 hover:text-white">
            <Link href="/dashboard">
              <LayoutDashboard className="w-4 h-4 mr-1" />
              {t("dashboard")}
            </Link>
          </Button>
          <Button asChild variant="ghost" size="sm" className="text-slate-400 hover:text-white">
            <Link href="/new-project">
              <Plus className="w-4 h-4 mr-1" />
              {t("newProject")}
            </Link>
          </Button>
          <LocaleSwitcher />
          <Button onClick={handleSignOut} variant="ghost" size="sm" className="text-slate-400 hover:text-white">
            <LogOut className="w-4 h-4 mr-1" />
            {t("signOut")}
          </Button>
        </div>
      </div>
    </nav>
  );
}
