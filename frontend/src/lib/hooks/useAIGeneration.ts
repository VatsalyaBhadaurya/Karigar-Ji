"use client";

import { useCallback, useRef, useState } from "react";
import { useUiStore } from "@/lib/stores/uiStore";
import { getRender } from "@/lib/api/render";
import { Render } from "@/lib/types";
import { useProjectStore } from "@/lib/stores/projectStore";

export function useRenderPoller(token: string) {
  const updateRender = useProjectStore((s) => s.updateRender);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const pollRender = useCallback((renderId: string) => {
    intervalRef.current = setInterval(async () => {
      const result = await getRender(renderId, token);
      if (result.error) {
        clearInterval(intervalRef.current!);
        return;
      }
      const render = result.data as Render;
      updateRender(render);
      if (render.render_status === "complete" || render.render_status === "error") {
        clearInterval(intervalRef.current!);
      }
    }, 3000);
  }, [token, updateRender]);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
  }, []);

  return { pollRender, stopPolling };
}
