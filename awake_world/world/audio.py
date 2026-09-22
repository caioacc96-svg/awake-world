from __future__ import annotations

from pathlib import Path


class AudioManager:
    """Failure-safe ambient audio with a cheap two-channel crossfade."""

    AMBIENT_VOLUME = 0.075

    def __init__(self) -> None:
        self.available = False
        self._ambient_channels: list[object] = []
        self._active_channel = 0
        self._fx = None
        self._current_ambient = ""
        self._fade_target = ""
        self._fade_elapsed = 0.0
        self._fade_duration = 0.0
        try:
            from PySide6.QtCore import QUrl
            from PySide6.QtMultimedia import QSoundEffect

            self._QUrl = QUrl
            for _ in range(2):
                channel = QSoundEffect()
                channel.setLoopCount(QSoundEffect.Infinite)
                channel.setVolume(0.0)
                self._ambient_channels.append(channel)
            self._fx = QSoundEffect()
            self._fx.setVolume(0.16)
            self.available = True
        except Exception:
            self.available = False

    @property
    def asset_dir(self) -> Path:
        return Path(__file__).resolve().parents[1] / "assets" / "audio"

    def _source_path(self, name: str) -> Path | None:
        path = self.asset_dir / f"{name}.wav"
        return path if path.exists() else None

    def set_ambient(self, name: str) -> None:
        if not self.available or not self._ambient_channels or name == self._current_ambient:
            return
        path = self._source_path(name)
        if path is None:
            return
        try:
            for channel in self._ambient_channels:
                channel.stop()
                channel.setVolume(0.0)
            channel = self._ambient_channels[self._active_channel]
            channel.setSource(self._QUrl.fromLocalFile(str(path)))
            channel.setVolume(self.AMBIENT_VOLUME)
            channel.play()
            self._current_ambient = name
            self._fade_target = ""
            self._fade_elapsed = 0.0
            self._fade_duration = 0.0
        except Exception:
            self.available = False

    def crossfade_to(self, name: str, duration: float = 0.62) -> None:
        if not self.available or not self._ambient_channels:
            return
        if name == self._current_ambient or name == self._fade_target:
            return
        path = self._source_path(name)
        if path is None:
            return
        if not self._current_ambient:
            self.set_ambient(name)
            return
        try:
            incoming_index = 1 - self._active_channel
            incoming = self._ambient_channels[incoming_index]
            incoming.stop()
            incoming.setSource(self._QUrl.fromLocalFile(str(path)))
            incoming.setVolume(0.0)
            incoming.play()
            self._fade_target = name
            self._fade_elapsed = 0.0
            self._fade_duration = max(0.08, float(duration))
        except Exception:
            self.available = False

    def tick(self, dt: float) -> None:
        if not self.available or not self._fade_target or len(self._ambient_channels) < 2:
            return
        try:
            self._fade_elapsed += max(0.0, float(dt))
            t = min(1.0, self._fade_elapsed / self._fade_duration)
            outgoing = self._ambient_channels[self._active_channel]
            incoming_index = 1 - self._active_channel
            incoming = self._ambient_channels[incoming_index]
            outgoing.setVolume(self.AMBIENT_VOLUME * (1.0 - t))
            incoming.setVolume(self.AMBIENT_VOLUME * t)
            if t >= 1.0:
                outgoing.stop()
                outgoing.setVolume(0.0)
                self._active_channel = incoming_index
                self._current_ambient = self._fade_target
                self._fade_target = ""
                self._fade_elapsed = 0.0
                self._fade_duration = 0.0
        except Exception:
            self.available = False

    def play_fx(self, name: str) -> None:
        if not self.available or self._fx is None:
            return
        path = self.asset_dir / f"{name}.wav"
        if not path.exists():
            return
        try:
            self._fx.setSource(self._QUrl.fromLocalFile(str(path)))
            self._fx.play()
        except Exception:
            self.available = False
