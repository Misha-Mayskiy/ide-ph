export type ThemePreset = "light" | "dark" | "high-contrast";
export type LayoutPreset = "classic" | "focus" | "split";
export type KeymapPreset = "vscode" | "vim" | "emacs";

export interface ThemeConfig {
  preset: ThemePreset;
}

export interface LayoutConfig {
  preset: LayoutPreset;
  ratios: Record<string, number>;
}

export interface PanelConfig {
  id: "explorer" | "terminal" | "tabs" | "statusBar";
  position: "left" | "right" | "bottom" | "top";
  visible: boolean;
  size: number;
}

export interface EditorConfig {
  fontSize: number;
}

export interface KeymapConfig {
  preset: KeymapPreset;
  overrides: Record<string, string>;
}

export interface IdeConfig {
  version: string;
  theme: ThemeConfig;
  layout: LayoutConfig;
  panels: PanelConfig[];
  editor: EditorConfig;
  keymap: KeymapConfig;
}

export interface GenerationCreateResponse {
  generationId: string;
  status: "queued" | "running" | "succeeded" | "failed";
  pollUrl: string;
}

export interface GenerationStatusResponse {
  status: "queued" | "running" | "succeeded" | "failed";
  progress: number;
  ideConfig?: IdeConfig;
  error?: { code: string; message: string; details?: unknown };
}

export interface Profile {
  id: string;
  name: string;
  ideConfig: IdeConfig;
  createdAt: string;
  updatedAt: string;
}
