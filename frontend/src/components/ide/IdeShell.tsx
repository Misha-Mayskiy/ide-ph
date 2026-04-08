import Editor from "@monaco-editor/react";

import type { IdeConfig } from "../../types/ide";

interface RuntimeFeatures {
  aiAssistant: boolean;
  eslint: boolean;
}

interface IdeShellProps {
  config: IdeConfig;
  features: RuntimeFeatures;
}

function panelVisible(config: IdeConfig, panelId: IdeConfig["panels"][number]["id"]): boolean {
  const panel = config.panels.find((item) => item.id === panelId);
  return panel?.visible ?? false;
}

export function IdeShell({ config, features }: IdeShellProps) {
  const theme = config.theme.preset === "high-contrast" ? "hc-black" : config.theme.preset === "light" ? "vs-light" : "vs-dark";
  const statusParts = [
    config.keymap.preset.toUpperCase(),
    "UTF-8",
    `AI ${features.aiAssistant ? "ON" : "OFF"}`,
    `ESLint ${features.eslint ? "ON" : "OFF"}`
  ];

  return (
    <section className={`card ide-shell layout-${config.layout.preset}`} data-testid="ide-shell">
      {panelVisible(config, "tabs") ? <div className="ide-tabs">index.tsx | settings.json</div> : null}

      <div className="ide-main">
        {panelVisible(config, "explorer") ? (
          <aside className="ide-explorer" aria-label="Explorer">
            <h3>Explorer</h3>
            <ul>
              <li>src/</li>
              <li>components/</li>
              <li>App.tsx</li>
            </ul>
          </aside>
        ) : null}

        <div className="ide-editor" aria-label="Editor">
          <Editor
            height="100%"
            language="typescript"
            theme={theme}
            options={{
              fontSize: config.editor.fontSize,
              minimap: { enabled: false },
              smoothScrolling: true
            }}
            defaultValue={'function hello() {\n  console.log("IDE Builder MVP");\n}\n'}
          />
        </div>
      </div>

      {panelVisible(config, "terminal") ? <div className="ide-terminal">$ npm run dev</div> : null}
      {panelVisible(config, "statusBar") ? <div className="ide-status">{statusParts.join(" | ")}</div> : null}
    </section>
  );
}
