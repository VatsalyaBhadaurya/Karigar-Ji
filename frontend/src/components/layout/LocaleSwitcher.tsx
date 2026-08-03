"use client";

import { useLocale } from "next-intl";
import { useRouter, usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";

export function LocaleSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const toggle = () => {
    const next = locale === "en" ? "hi" : "en";
    const newPath = pathname.replace(`/${locale}`, `/${next}`);
    router.push(newPath);
  };

  return (
    <Button onClick={toggle} variant="ghost" size="sm" className="text-slate-400 hover:text-white font-mono text-xs">
      {locale === "en" ? "हिं" : "EN"}
    </Button>
  );
}
