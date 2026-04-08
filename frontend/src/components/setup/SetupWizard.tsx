import { FormEvent, useMemo, useState } from "react";

import { DEFAULT_SETUP_OPTIONS, type SetupOptions } from "../../types/setup";

interface SetupWizardProps {
  status: string;
  progress: number;
  error: string | null;
  defaultOptions?: SetupOptions;
  jwtToken: string;
  isJwtProvided: boolean;
  onJwtChange: (value: string) => void;
  onJwtApply: () => void;
  onUseDemoJwt?: () => void;
  onGenerate: (options: SetupOptions, prompt: string) => Promise<void>;
}

export function SetupWizard({
  status,
  progress,
  error,
  defaultOptions,
  jwtToken,
  isJwtProvided,
  onJwtChange,
  onJwtApply,
  onUseDemoJwt,
  onGenerate
}: SetupWizardProps) {
  const [step, setStep] = useState<"options" | "prompt">("options");
  const [options, setOptions] = useState<SetupOptions>(defaultOptions ?? DEFAULT_SETUP_OPTIONS);
  const [prompt, setPrompt] = useState("Build me a focused IDE for TypeScript web app development");

  const summary = useMemo(
    () =>
      [
        `theme: ${options.theme}`,
        `layout: ${options.layout}`,
        `keymap: ${options.keymap}`,
        `font: ${options.fontSize}`,
        `AI: ${options.aiAssistant ? "on" : "off"}`,
        `ESLint: ${options.eslint ? "on" : "off"}`
      ].join(" | "),
    [options]
  );

  async function handleGenerate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!isJwtProvided) {
      return;
    }
    await onGenerate(options, prompt);
  }

  return (
    <section className="card setup-card">
      <h2>IDE Setup</h2>

      {step === "options" ? (
        <div className="setup-grid">
          <label>
            Theme
            <select
              value={options.theme}
              onChange={(event) =>
                setOptions((prev) => ({ ...prev, theme: event.target.value as SetupOptions["theme"] }))
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
              value={options.layout}
              onChange={(event) =>
                setOptions((prev) => ({ ...prev, layout: event.target.value as SetupOptions["layout"] }))
              }
            >
              <option value="classic">classic</option>
              <option value="focus">focus</option>
              <option value="split">split</option>
            </select>
          </label>

          <label>
            Keymap
            <select
              value={options.keymap}
              onChange={(event) =>
                setOptions((prev) => ({ ...prev, keymap: event.target.value as SetupOptions["keymap"] }))
              }
            >
              <option value="vscode">vscode</option>
              <option value="vim">vim</option>
              <option value="emacs">emacs</option>
            </select>
          </label>

          <label>
            Font size
            <input
              type="number"
              min={10}
              max={32}
              value={options.fontSize}
              onChange={(event) => setOptions((prev) => ({ ...prev, fontSize: Number(event.target.value) }))}
            />
          </label>

          <label>
            Locale
            <select
              value={options.locale}
              onChange={(event) =>
                setOptions((prev) => ({ ...prev, locale: event.target.value as SetupOptions["locale"] }))
              }
            >
              <option value="ru">ru</option>
              <option value="en">en</option>
            </select>
          </label>

          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={options.aiAssistant}
              onChange={(event) => setOptions((prev) => ({ ...prev, aiAssistant: event.target.checked }))}
            />
            Connect AI assistant
          </label>

          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={options.eslint}
              onChange={(event) => setOptions((prev) => ({ ...prev, eslint: event.target.checked }))}
            />
            Enable ESLint
          </label>

          <label>
            JWT token
            <input
              value={jwtToken}
              onChange={(event) => onJwtChange(event.target.value)}
              onBlur={onJwtApply}
              placeholder="Paste JWT with sub claim"
            />
          </label>

          <div className="row">
            {onUseDemoJwt ? (
              <button type="button" onClick={onUseDemoJwt}>
                Use demo token
              </button>
            ) : null}
            <button type="button" onClick={() => setStep("prompt")} disabled={!isJwtProvided}>
              Next: Write Prompt
            </button>
          </div>

          {!isJwtProvided ? <div className="error">JWT token is required before generation.</div> : null}
        </div>
      ) : (
        <form onSubmit={handleGenerate} className="setup-prompt-form">
          <div className="setup-summary">{summary}</div>

          <label>
            Prompt
            <textarea
              rows={6}
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              placeholder="Describe the IDE you want"
            />
          </label>

          <div className="row">
            <button type="button" onClick={() => setStep("options")}>
              Back to options
            </button>
            <button type="submit" disabled={!isJwtProvided || status === "queued" || status === "running"}>
              {status === "queued" || status === "running" ? "Generating..." : "Generate IDE"}
            </button>
          </div>

          <div className="terminal-status">
            <div>Status: {status}</div>
            <div>Progress: {progress}%</div>
            {error ? <div className="error">{error}</div> : null}
          </div>
        </form>
      )}
    </section>
  );
}
