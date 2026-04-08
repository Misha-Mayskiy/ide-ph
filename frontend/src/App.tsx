import { useMemo, useState } from "react";

import {
  createProfile,
  deleteProfile,
  getJwtToken,
  getProfile,
  listProfiles,
  setJwtToken,
  updateProfile
} from "./api/client";
import { IdeShell } from "./components/ide/IdeShell";
import { TweaksPanel } from "./components/ide/TweaksPanel";
import { ProfilesPanel } from "./components/profiles/ProfilesPanel";
import { SetupWizard } from "./components/setup/SetupWizard";
import { useGeneration } from "./hooks/useGeneration";
import { defaultIdeConfig, normalizeIdeConfig } from "./lib/config";
import type { IdeConfig, Profile } from "./types/ide";
import { DEFAULT_SETUP_OPTIONS, type SetupOptions } from "./types/setup";

const FALLBACK_DEMO_JWT = import.meta.env.VITE_DEMO_JWT ?? "";

function buildGenerationPrompt(options: SetupOptions, prompt: string): string {
  return [
    prompt,
    "",
    "Selected IDE options:",
    `theme=${options.theme}`,
    `layout=${options.layout}`,
    `keymap=${options.keymap}`,
    `font_size=${options.fontSize}`,
    `ai_assistant=${options.aiAssistant ? "enabled" : "disabled"}`,
    `eslint=${options.eslint ? "enabled" : "disabled"}`
  ].join("\n");
}

function applySetupOptions(config: IdeConfig, options: SetupOptions): IdeConfig {
  return normalizeIdeConfig({
    ...config,
    theme: { ...config.theme, preset: options.theme },
    layout: { ...config.layout, preset: options.layout },
    editor: { ...config.editor, fontSize: options.fontSize },
    keymap: { ...config.keymap, preset: options.keymap }
  });
}

export default function App() {
  const [jwtInput, setJwtInput] = useState(() => localStorage.getItem("jwt_token") ?? FALLBACK_DEMO_JWT);
  const [config, setConfig] = useState<IdeConfig>(defaultIdeConfig());
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [selectedProfileId, setSelectedProfileId] = useState<string | null>(null);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [hasGenerated, setHasGenerated] = useState(false);
  const [setupOptions, setSetupOptions] = useState<SetupOptions>(DEFAULT_SETUP_OPTIONS);

  const generation = useGeneration();

  const isJwtProvided = useMemo(() => Boolean((jwtInput || getJwtToken()).trim()), [jwtInput]);

  function applyJwtToken(): boolean {
    const candidate = jwtInput.trim() || getJwtToken().trim();
    if (!candidate) {
      setProfileError("JWT token is required. Paste token or use demo token.");
      setJwtToken("");
      return false;
    }

    setJwtToken(candidate);
    setJwtInput(candidate);
    setProfileError(null);
    return true;
  }

  function handleUseDemoJwt() {
    if (!FALLBACK_DEMO_JWT) {
      setProfileError("Demo JWT is not configured.");
      return;
    }

    setJwtInput(FALLBACK_DEMO_JWT);
    setJwtToken(FALLBACK_DEMO_JWT);
    setProfileError(null);
  }

  async function refreshProfiles() {
    if (!applyJwtToken()) {
      return;
    }

    try {
      const nextProfiles = await listProfiles();
      setProfiles(nextProfiles);
      setProfileError(null);
    } catch (error) {
      setProfileError(error instanceof Error ? error.message : "Failed to load profiles");
    }
  }

  const cssThemeClass = useMemo(() => `theme-${config.theme.preset}`, [config.theme.preset]);

  async function handleGenerate(options: SetupOptions, prompt: string) {
    if (!applyJwtToken()) {
      return;
    }

    setSetupOptions(options);

    const generationPrompt = buildGenerationPrompt(options, prompt);
    const generatedConfig = await generation.generate(generationPrompt, options.locale);

    if (!generatedConfig) {
      return;
    }

    const nextConfig = applySetupOptions(generatedConfig, options);
    setConfig(nextConfig);
    setHasGenerated(true);
    await refreshProfiles();
  }

  async function handleCreateProfile(name: string) {
    if (!applyJwtToken()) {
      return;
    }
    const created = await createProfile(name, normalizeIdeConfig(config));
    setSelectedProfileId(created.id);
    await refreshProfiles();
  }

  async function handleOpenProfile(profileId: string) {
    if (!applyJwtToken()) {
      return;
    }
    const profile = await getProfile(profileId);
    setSelectedProfileId(profile.id);
    setConfig(normalizeIdeConfig(profile.ideConfig));
    setHasGenerated(true);
  }

  async function handleUpdateProfile(profileId: string, name: string) {
    if (!applyJwtToken()) {
      return;
    }
    await updateProfile(profileId, { name, ideConfig: normalizeIdeConfig(config) });
    setSelectedProfileId(profileId);
    await refreshProfiles();
  }

  async function handleDeleteProfile(profileId: string) {
    if (!applyJwtToken()) {
      return;
    }
    await deleteProfile(profileId);
    if (selectedProfileId === profileId) {
      setSelectedProfileId(null);
    }
    await refreshProfiles();
  }

  if (!hasGenerated) {
    return (
      <main className="app app-onboarding">
        <section className="onboarding-column">
          <SetupWizard
            status={generation.status}
            progress={generation.progress}
            error={generation.error}
            defaultOptions={setupOptions}
            jwtToken={jwtInput}
            isJwtProvided={isJwtProvided}
            onJwtChange={setJwtInput}
            onJwtApply={applyJwtToken}
            onUseDemoJwt={FALLBACK_DEMO_JWT ? handleUseDemoJwt : undefined}
            onGenerate={handleGenerate}
          />
          {profileError ? <div className="card error">{profileError}</div> : null}
        </section>
      </main>
    );
  }

  return (
    <main className={`app ${cssThemeClass}`}>
      <header className="app-header card">
        <h1>IDE Builder MVP</h1>
        <button type="button" onClick={() => setHasGenerated(false)}>
          New IDE Setup
        </button>
      </header>

      <section className="left-column">
        <SetupWizard
          status={generation.status}
          progress={generation.progress}
          error={generation.error}
          defaultOptions={setupOptions}
          jwtToken={jwtInput}
          isJwtProvided={isJwtProvided}
          onJwtChange={setJwtInput}
          onJwtApply={applyJwtToken}
          onUseDemoJwt={FALLBACK_DEMO_JWT ? handleUseDemoJwt : undefined}
          onGenerate={handleGenerate}
        />

        <ProfilesPanel
          profiles={profiles}
          selectedId={selectedProfileId}
          onCreate={handleCreateProfile}
          onOpen={handleOpenProfile}
          onUpdate={handleUpdateProfile}
          onDelete={handleDeleteProfile}
        />

        {profileError ? <div className="card error">{profileError}</div> : null}
      </section>

      <section className="main-column">
        <IdeShell
          config={config}
          features={{ aiAssistant: setupOptions.aiAssistant, eslint: setupOptions.eslint }}
        />
      </section>

      <section className="right-column">
        <TweaksPanel config={config} onChange={(next) => setConfig(normalizeIdeConfig(next))} />
      </section>
    </main>
  );
}
