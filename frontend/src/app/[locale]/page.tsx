import { useTranslations } from "next-intl";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function LandingPage() {
  const t = useTranslations("common");

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 text-white px-4">
      <div className="text-center max-w-3xl">
        <h1 className="text-6xl font-bold tracking-tight mb-4">{t("appName")}</h1>
        <p className="text-xl text-slate-400 mb-8">{t("tagline")}</p>
        <p className="text-slate-300 mb-10 text-lg leading-relaxed">
          Upload a sketch. Get photorealistic renders, tech packs, pattern drafts,
          and manufacturing docs — powered by AI.
        </p>
        <div className="flex gap-4 justify-center">
          <Button asChild size="lg" className="bg-white text-slate-900 hover:bg-slate-100 font-semibold px-8">
            <Link href="/auth/login">Get Started</Link>
          </Button>
          <Button asChild variant="outline" size="lg" className="border-slate-600 text-white hover:bg-slate-800 px-8">
            <Link href="/auth/signup">Create Account</Link>
          </Button>
        </div>
      </div>
      <div className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-6 text-center text-sm text-slate-400 max-w-2xl">
        {["Photorealistic Renders", "Tech Packs", "Pattern Drafts", "Manufacturing Docs"].map((feat) => (
          <div key={feat} className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
            {feat}
          </div>
        ))}
      </div>
    </main>
  );
}
