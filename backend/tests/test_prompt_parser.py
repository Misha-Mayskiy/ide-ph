import pytest

from app.core.config import Settings
from app.services.prompt_parser import parse_prompt


@pytest.mark.asyncio
async def test_prompt_parser_detects_theme_layout_and_keymap() -> None:
    settings = Settings(openai_api_key=None)
    parsed = await parse_prompt("Make dark split layout and vim keymap", "ru", settings)

    assert parsed["theme"]["preset"] == "dark"
    assert parsed["layout"]["preset"] == "split"
    assert parsed["keymap"]["preset"] == "vim"


@pytest.mark.asyncio
async def test_prompt_parser_detects_font_size() -> None:
    settings = Settings(openai_api_key=None)
    parsed = await parse_prompt("font size 18", "en", settings)

    assert parsed["editor"]["fontSize"] == 18
