from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PySide6.QtWidgets import QApplication


class ThemeEngine:
    """Loads design tokens and applies tokenized QSS themes."""

    def __init__(self) -> None:
        self.base = Path(__file__).resolve().parents[1]
        self.token_dir = self.base / "tokens"
        self.theme_dir = Path(__file__).resolve().parent
        self.tokens = self._load_tokens()
        self.current = "light"

    def _load_tokens(self) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        for path in sorted(self.token_dir.glob("*.json")):
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            merged.update(data)
        return merged

    def color(self, name: str) -> str:
        value = self.tokens.get(name)
        if not isinstance(value, str) or not value.startswith("#"):
            raise KeyError(f"Unknown color token: {name}")
        return value

    def value(self, name: str, default: Any = None) -> Any:
        return self.tokens.get(name, default)

    def stylesheet(self, theme: str) -> str:
        path = self.theme_dir / f"{theme}.qss"
        if not path.exists():
            raise ValueError(f"Unknown theme: {theme}")
        qss = path.read_text(encoding="utf-8")
        for key, value in self.tokens.items():
            qss = qss.replace("{{" + key + "}}", str(value))
        return qss

    def apply(self, app: QApplication, theme: str) -> None:
        app.setStyleSheet(self.stylesheet(theme))
        self.current = theme
