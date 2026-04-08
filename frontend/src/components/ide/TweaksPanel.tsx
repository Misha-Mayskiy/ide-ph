import type { IdeConfig, KeymapPreset, LayoutPreset, ThemePreset } from "../../types/ide";

interface TweaksPanelProps {
  config: IdeConfig;
  onChange: (next: IdeConfig) => void;
}

export function TweaksPanel({ config, onChange }: TweaksPanelProps) {
  return (
    <section className="card tweaks-card">
      <h2>Tweaks</h2>

      <label>
        Theme
        <select
          value={config.theme.preset}
          onChange={(event) =>
            onChange({
              ...config,
              theme: { preset: event.target.value as ThemePreset }
            })
          }
        >
          <option value="light">light</option>
          <option value="dark">dark</option>
          <option value="high-contrast">high-contrast</option>
        </select>
      </label>

      <label>
        Layout
        <select
          value={config.layout.preset}
          onChange={(event) =>
            onChange({
              ...config,
              layout: { ...config.layout, preset: event.target.value as LayoutPreset }
            })
          }
        >
          <option value="classic">classic</option>
          <option value="focus">focus</option>
          <option value="split">split</option>
        </select>
      </label>

      <label>
        Font Size
        <input
          type="number"
          min={10}
          max={32}
          value={config.editor.fontSize}
          onChange={(event) =>
            onChange({
              ...config,
              editor: { fontSize: Number(event.target.value) }
            })
          }
        />
      </label>

      <label>
        Keymap
        <select
          value={config.keymap.preset}
          onChange={(event) =>
            onChange({
              ...config,
              keymap: { ...config.keymap, preset: event.target.value as KeymapPreset }
            })
          }
        >
          <option value="vscode">vscode</option>
          <option value="vim">vim</option>
          <option value="emacs">emacs</option>
        </select>
      </label>
    </section>
  );
}
