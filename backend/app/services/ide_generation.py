from typing import Any

from app.core.config import Settings
from app.schemas.ide_config import IdeConfig, default_ide_config, normalize_ide_config
from app.services.prompt_parser import parse_prompt


async def generate_ide_config(prompt: str, locale: str, settings: Settings) -> IdeConfig:
    try:
        parsed: dict[str, Any] = await parse_prompt(prompt, locale, settings)
        return normalize_ide_config(parsed)
    except Exception:
        return default_ide_config()
