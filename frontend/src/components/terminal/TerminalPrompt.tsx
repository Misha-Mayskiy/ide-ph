import { FormEvent, useState } from "react";

interface TerminalPromptProps {
  onSubmit: (prompt: string, locale: "ru" | "en") => Promise<void>;
  status: string;
  progress: number;
  error: string | null;
}

export function TerminalPrompt({ onSubmit, status, progress, error }: TerminalPromptProps) {
  const [prompt, setPrompt] = useState("Dark split IDE with vim keymap and font 15");
  const [locale, setLocale] = useState<"ru" | "en">("ru");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit(prompt, locale);
  }

  return (
    <section className="card terminal-card">
      <h2>Prompt Terminal</h2>
      <form onSubmit={handleSubmit} className="terminal-form">
        <div className="field-row">
          <label htmlFor="prompt">IDE description</label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            rows={5}
            placeholder="Describe theme, layout, panels and keymap"
          />
        </div>
        <div className="row">
          <label htmlFor="locale">Locale</label>
          <select id="locale" value={locale} onChange={(event) => setLocale(event.target.value as "ru" | "en")}>
            <option value="ru">ru</option>
            <option value="en">en</option>
          </select>
        </div>
        <button type="submit" disabled={status === "queued" || status === "running"}>
          {status === "queued" || status === "running" ? "Generating..." : "Generate IDE"}
        </button>
      </form>
      <div className="terminal-status">
        <div>Status: {status}</div>
        <div>Progress: {progress}%</div>
        {error ? <div className="error">{error}</div> : null}
      </div>
    </section>
  );
}
