import type { GenerationStatusResponse } from "../types/ide";

export async function pollGeneration(
  getStatus: () => Promise<GenerationStatusResponse>,
  onTick: (payload: GenerationStatusResponse) => void,
  intervalMs = 1200,
  timeoutMs = 30000
): Promise<GenerationStatusResponse> {
  const started = Date.now();

  while (Date.now() - started < timeoutMs) {
    const payload = await getStatus();
    onTick(payload);

    if (payload.status === "succeeded" || payload.status === "failed") {
      return payload;
    }

    await new Promise((resolve) => setTimeout(resolve, intervalMs));
  }

  throw new Error("Generation timeout");
}
