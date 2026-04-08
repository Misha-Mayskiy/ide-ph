import { pollGeneration } from "../api/pollGeneration";


describe("pollGeneration", () => {
  it("returns terminal payload", async () => {
    const states = [
      { status: "queued", progress: 0 },
      { status: "running", progress: 50 },
      { status: "succeeded", progress: 100, ideConfig: { version: "1.0" } }
    ];

    let call = 0;
    const ticks: string[] = [];

    const result = await pollGeneration(
      async () => states[call++] as never,
      (payload) => ticks.push(payload.status),
      1,
      2000
    );

    expect(result.status).toBe("succeeded");
    expect(ticks).toEqual(["queued", "running", "succeeded"]);
  });
});
