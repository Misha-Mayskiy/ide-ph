import { useCallback, useState } from "react";

import { createGeneration, getGeneration } from "../api/client";
import { pollGeneration } from "../api/pollGeneration";
import { normalizeIdeConfig } from "../lib/config";
import type { IdeConfig } from "../types/ide";

export function useGeneration() {
  const [generationId, setGenerationId] = useState<string | null>(null);
  const [status, setStatus] = useState<"idle" | "queued" | "running" | "succeeded" | "failed">("idle");
  const [progress, setProgress] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);

  const generate = useCallback(async (prompt: string, locale: "ru" | "en"): Promise<IdeConfig | null> => {
    setError(null);
    setStatus("queued");
    setProgress(0);

    const created = await createGeneration(prompt, locale);
    setGenerationId(created.generationId);

    const finalPayload = await pollGeneration(
      () => getGeneration(created.generationId),
      (payload) => {
        setStatus(payload.status);
        setProgress(payload.progress);
      }
    );

    if (finalPayload.status === "failed") {
      setError(finalPayload.error?.message ?? "Generation failed");
      return null;
    }

    setStatus("succeeded");
    return normalizeIdeConfig(finalPayload.ideConfig ?? {});
  }, []);

  return {
    generationId,
    status,
    progress,
    error,
    generate
  };
}
