import { expect, test } from "@playwright/test";


test("prompt -> generation -> save profile -> reopen", async ({ page }) => {
  let profileCounter = 0;
  const profiles: Array<{ id: string; name: string; ideConfig: any; createdAt: string; updatedAt: string }> = [];

  await page.route("**/api/v1/profiles", async (route) => {
    const request = route.request();
    if (request.method() === "GET") {
      await route.fulfill({ json: { items: profiles } });
      return;
    }

    if (request.method() === "POST") {
      profileCounter += 1;
      const body = JSON.parse(request.postData() ?? "{}");
      const now = new Date().toISOString();
      const profile = {
        id: `p-${profileCounter}`,
        name: body.name,
        ideConfig: body.ideConfig,
        createdAt: now,
        updatedAt: now
      };
      profiles.unshift(profile);
      await route.fulfill({ json: profile, status: 201 });
      return;
    }

    await route.fulfill({ status: 404 });
  });

  await page.route("**/api/v1/profiles/*", async (route) => {
    const request = route.request();
    const id = request.url().split("/").pop();
    const found = profiles.find((profile) => profile.id === id);

    if (request.method() === "GET") {
      if (!found) {
        await route.fulfill({ status: 404, json: { code: "not_found", message: "not found" } });
        return;
      }
      await route.fulfill({ json: found });
      return;
    }

    if (request.method() === "PUT") {
      if (!found) {
        await route.fulfill({ status: 404, json: { code: "not_found", message: "not found" } });
        return;
      }
      const body = JSON.parse(request.postData() ?? "{}");
      found.name = body.name ?? found.name;
      found.ideConfig = body.ideConfig ?? found.ideConfig;
      found.updatedAt = new Date().toISOString();
      await route.fulfill({ json: found });
      return;
    }

    if (request.method() === "DELETE") {
      const index = profiles.findIndex((profile) => profile.id === id);
      if (index >= 0) {
        profiles.splice(index, 1);
      }
      await route.fulfill({ status: 204, body: "" });
      return;
    }

    await route.fulfill({ status: 404 });
  });

  await page.route("**/api/v1/generations", async (route) => {
    await route.fulfill({
      status: 201,
      json: { generationId: "gen-1", status: "queued", pollUrl: "http://localhost:8000/api/v1/generations/gen-1" }
    });
  });

  let pollCount = 0;
  await page.route("**/api/v1/generations/gen-1", async (route) => {
    pollCount += 1;
    if (pollCount < 2) {
      await route.fulfill({ json: { status: "running", progress: 50 } });
      return;
    }

    await route.fulfill({
      json: {
        status: "succeeded",
        progress: 100,
        ideConfig: {
          version: "1.0",
          theme: { preset: "dark" },
          layout: { preset: "split", ratios: { left: 0.2, center: 0.6, right: 0.2 } },
          panels: [
            { id: "explorer", position: "left", visible: true, size: 280 },
            { id: "terminal", position: "bottom", visible: true, size: 260 },
            { id: "tabs", position: "top", visible: true, size: 120 },
            { id: "statusBar", position: "bottom", visible: true, size: 40 }
          ],
          editor: { fontSize: 14 },
          keymap: { preset: "vim", overrides: {} }
        },
        error: null
      }
    });
  });

  await page.goto("/");

  await page.getByRole("button", { name: "Generate IDE" }).click();
  await expect(page.getByText("Status: succeeded")).toBeVisible();

  await page.getByRole("button", { name: "Save Current" }).click();
  await expect(page.getByText("My profile")).toBeVisible();

  await page.getByRole("button", { name: "Open" }).first().click();
  await expect(page.getByTestId("ide-shell")).toBeVisible();
});
