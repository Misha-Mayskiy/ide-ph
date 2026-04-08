from app.schemas.ide_config import normalize_ide_config


def test_normalizer_applies_defaults_and_ignores_unknowns() -> None:
    config = normalize_ide_config(
        {
            "theme": {"preset": "light", "foo": "bar"},
            "editor": {"fontSize": 16},
            "unknownRoot": 123,
        }
    )

    assert config.theme.preset == "light"
    assert config.editor.fontSize == 16
    assert len(config.panels) == 4


def test_normalizer_resolves_duplicate_positions() -> None:
    config = normalize_ide_config(
        {
            "panels": [
                {"id": "explorer", "position": "left", "visible": True, "size": 250},
                {"id": "terminal", "position": "left", "visible": True, "size": 300},
            ]
        }
    )

    explorer = next(p for p in config.panels if p.id == "explorer")
    terminal = next(p for p in config.panels if p.id == "terminal")

    assert explorer.position == "left"
    assert terminal.position == "bottom"
