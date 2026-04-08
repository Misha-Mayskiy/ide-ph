import { defaultIdeConfig, normalizeIdeConfig } from "../lib/config";


describe("normalizeIdeConfig", () => {
  it("fills defaults and drops invalid values", () => {
    const result = normalizeIdeConfig({
      theme: { preset: "light", invalid: true },
      editor: { fontSize: 16 },
      extra: "value"
    });

    expect(result.theme.preset).toBe("light");
    expect(result.editor.fontSize).toBe(16);
    expect(result.panels).toHaveLength(4);
  });

  it("hides explorer and terminal in focus layout", () => {
    const result = normalizeIdeConfig({ layout: { preset: "focus", ratios: { left: 0.2, center: 0.6, right: 0.2 } } });

    expect(result.panels.find((panel) => panel.id === "explorer")?.visible).toBe(false);
    expect(result.panels.find((panel) => panel.id === "terminal")?.visible).toBe(false);
  });

  it("returns valid default config", () => {
    const defaults = defaultIdeConfig();
    expect(defaults.keymap.preset).toBe("vscode");
  });
});
