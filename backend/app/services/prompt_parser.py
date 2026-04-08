import json
import re
from typing import Any

from app.core.config import Settings


DARK_HINTS = ("dark", "temn")
LIGHT_HINTS = ("light", "svetl")
HC_HINTS = ("high contrast", "contrast")

FOCUS_HINTS = ("focus", "minimal", "no panels")
SPLIT_HINTS = ("split", "two columns")

VIM_HINTS = ("vim",)
EMACS_HINTS = ("emacs",)


async def parse_prompt(prompt: str, locale: str, settings: Settings) -> dict[str, Any]:
    llm_output = await _try_llm(prompt, locale, settings)
    if isinstance(llm_output, dict):
        return llm_output

    return _heuristic_parse(prompt)


async def _try_llm(prompt: str, locale: str, settings: Settings) -> dict[str, Any] | None:
    if not settings.openai_api_key:
        return None

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        completion = await client.chat.completions.create(
            model=settings.openai_model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Return only JSON object with optional keys: theme, layout, panels, editor, keymap."
                        " theme.preset in [light,dark,high-contrast],"
                        " layout.preset in [classic,focus,split],"
                        " keymap.preset in [vscode,vim,emacs]."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps({"locale": locale, "prompt": prompt}, ensure_ascii=False),
                },
            ],
        )
        content = completion.choices[0].message.content
        if not content:
            return None
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        return None

    return None


def _heuristic_parse(prompt: str) -> dict[str, Any]:
    text = prompt.lower()
    result: dict[str, Any] = {}

    if any(h in text for h in DARK_HINTS):
        result["theme"] = {"preset": "dark"}
    elif any(h in text for h in LIGHT_HINTS):
        result["theme"] = {"preset": "light"}
    elif any(h in text for h in HC_HINTS):
        result["theme"] = {"preset": "high-contrast"}

    if any(h in text for h in FOCUS_HINTS):
        result["layout"] = {"preset": "focus"}
    elif any(h in text for h in SPLIT_HINTS):
        result["layout"] = {"preset": "split"}

    if any(h in text for h in VIM_HINTS):
        result["keymap"] = {"preset": "vim"}
    elif any(h in text for h in EMACS_HINTS):
        result["keymap"] = {"preset": "emacs"}

    font_match = re.search(r"(?:font|shrift)\s*(?:size)?\s*(\d{2})", text)
    if font_match:
        result.setdefault("editor", {})["fontSize"] = int(font_match.group(1))

    if "hide terminal" in text:
        result["panels"] = [{"id": "terminal", "position": "bottom", "visible": False, "size": 240}]

    return result
