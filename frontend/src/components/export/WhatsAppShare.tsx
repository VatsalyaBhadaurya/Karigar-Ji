"use client";

import { useTranslations } from "next-intl";
import { ProjectFull } from "@/lib/types";
import { Button } from "@/components/ui/button";

interface Props {
  project: ProjectFull;
  shareUrl?: string;
}

export function WhatsAppShare({ project, shareUrl }: Props) {
  const t = useTranslations("export");

  const handleShare = () => {
    const url = shareUrl || window.location.href;
    const message = encodeURIComponent(`${t("whatsappMessage")}${url}`);
    window.open(`https://wa.me/?text=${message}`, "_blank");
  };

  return (
    <Button
      onClick={handleShare}
      className="bg-[#25D366] hover:bg-[#1da851] text-white font-semibold w-full"
    >
      {t("whatsapp")}
    </Button>
  );
}
