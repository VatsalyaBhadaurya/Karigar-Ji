"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { createClient } from "@/lib/supabase/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function LoginForm() {
  const t = useTranslations("auth");
  const router = useRouter();
  const supabase = createClient();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) {
      setError(error.message);
      setLoading(false);
      return;
    }
    router.push("/dashboard");
  };

  const handleGoogle = async () => {
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: `${window.location.origin}/api/auth/callback` },
    });
  };

  return (
    <Card className="w-full max-w-md bg-slate-900 border-slate-700 text-white">
      <CardHeader className="text-center">
        <CardTitle className="text-2xl font-bold">KarigarJi</CardTitle>
        <p className="text-slate-400 text-sm">{t("login")}</p>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <Label className="text-slate-300">{t("email")}</Label>
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="mt-1 bg-slate-800 border-slate-600 text-white"
            />
          </div>
          <div>
            <Label className="text-slate-300">{t("password")}</Label>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="mt-1 bg-slate-800 border-slate-600 text-white"
            />
          </div>
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <Button type="submit" disabled={loading} className="w-full bg-white text-slate-900 hover:bg-slate-100 font-semibold">
            {loading ? "Signing in..." : t("login")}
          </Button>
        </form>
        <div className="mt-4 text-center">
          <p className="text-slate-500 text-xs mb-3">{t("orContinueWith")}</p>
          <Button onClick={handleGoogle} variant="outline" className="w-full border-slate-600 text-white hover:bg-slate-800">
            {t("google")}
          </Button>
        </div>
        <p className="mt-6 text-center text-slate-400 text-sm">
          {t("noAccount")}{" "}
          <Link href="/auth/signup" className="text-white underline">
            {t("signup")}
          </Link>
        </p>
      </CardContent>
    </Card>
  );
}
