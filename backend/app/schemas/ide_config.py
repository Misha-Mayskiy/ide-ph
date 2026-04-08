from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ThemePreset = Literal["light", "dark", "high-contrast"]
LayoutPreset = Literal["classic", "focus", "split"]
PanelId = Literal["explorer", "terminal", "tabs", "statusBar"]
PanelPosition = Literal["left", "right", "bottom", "top"]
KeymapPreset = Literal["vscode", "vim", "emacs"]


class ThemeConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    preset: ThemePreset = "dark"


class LayoutConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    preset: LayoutPreset = "classic"
    ratios: dict[str, float] = Field(default_factory=lambda: {"left": 0.2, "center": 0.6, "right": 0.2})


class PanelConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: PanelId
    position: PanelPosition
    visible: bool = True
    size: int = Field(default=300, ge=24, le=800)


class EditorConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    fontSize: int = Field(default=14, ge=10, le=32)


class KeymapConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    preset: KeymapPreset = "vscode"
    overrides: dict[str, str] = Field(default_factory=dict)


class IdeConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    version: str = "1.0"
    theme: ThemeConfig = Field(default_factory=ThemeConfig)
    layout: LayoutConfig = Field(default_factory=LayoutConfig)
    panels: list[PanelConfig] = Field(default_factory=list)
    editor: EditorConfig = Field(default_factory=EditorConfig)
    keymap: KeymapConfig = Field(default_factory=KeymapConfig)


def default_ide_config() -> IdeConfig:
    return IdeConfig(
        theme=ThemeConfig(preset="dark"),
        layout=LayoutConfig(preset="classic", ratios={"left": 0.22, "center": 0.58, "right": 0.2}),
        panels=[
            PanelConfig(id="explorer", position="left", visible=True, size=280),
            PanelConfig(id="terminal", position="bottom", visible=True, size=260),
            PanelConfig(id="tabs", position="top", visible=True, size=120),
            PanelConfig(id="statusBar", position="bottom", visible=True, size=40),
        ],
        editor=EditorConfig(fontSize=14),
        keymap=KeymapConfig(preset="vscode", overrides={}),
    )


def normalize_ide_config(raw: dict[str, Any] | IdeConfig | None) -> IdeConfig:
    base = default_ide_config().model_dump(mode="json")
    incoming = raw.model_dump(mode="json") if isinstance(raw, IdeConfig) else (raw or {})

    merged = {
        **base,
        **{k: v for k, v in incoming.items() if k in base},
    }

    # merge nested maps
    for key in ("theme", "layout", "editor", "keymap"):
        if key in incoming and isinstance(incoming[key], dict):
            merged[key] = {**base[key], **incoming[key]}

    if "panels" in incoming and isinstance(incoming["panels"], list):
        merged["panels"] = incoming["panels"]

    config = IdeConfig.model_validate(merged)
    return _resolve_conflicts(config)


def _resolve_conflicts(config: IdeConfig) -> IdeConfig:
    defaults = {p.id: p for p in default_ide_config().panels}
    used_positions: set[str] = set()
    resolved: list[PanelConfig] = []

    for panel in config.panels:
        default_panel = defaults.get(panel.id)
        if default_panel is None:
            continue

        position = panel.position
        if panel.id in {"explorer", "terminal"} and position in used_positions:
            position = default_panel.position

        used_positions.add(position)
        resolved.append(
            PanelConfig(
                id=panel.id,
                position=position,
                visible=panel.visible,
                size=panel.size,
            )
        )

    missing_ids = {"explorer", "terminal", "tabs", "statusBar"} - {p.id for p in resolved}
    for panel_id in sorted(missing_ids):
        resolved.append(defaults[panel_id])

    if config.layout.preset == "focus":
        resolved = [
            PanelConfig(
                id=p.id,
                position=p.position,
                visible=False if p.id in {"explorer", "terminal"} else p.visible,
                size=p.size,
            )
            for p in resolved
        ]

    return IdeConfig(
        version=config.version,
        theme=config.theme,
        layout=config.layout,
        panels=resolved,
        editor=config.editor,
        keymap=config.keymap,
    )

