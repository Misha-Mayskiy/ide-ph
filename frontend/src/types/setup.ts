import type { KeymapPreset, LayoutPreset, ThemePreset } from "./ide";

export interface SetupOptions {
  theme: ThemePreset;
  layout: LayoutPreset;
  keymap: KeymapPreset;
  fontSize: number;
  locale: "ru" | "en";
  aiAssistant: boolean;
  eslint: boolean;
}

export const DEFAULT_SETUP_OPTIONS: SetupOptions = {
  theme: "dark",
  layout: "classic",
  keymap: "vscode",
  fontSize: 14,
  locale: "ru",
  aiAssistant: true,
  eslint: true
};
