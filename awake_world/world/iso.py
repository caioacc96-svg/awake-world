from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QPointF


@dataclass(frozen=True)
class IsoMetrics:
    tile_width: float = 96.0
    tile_height: float = 48.0
    elevation_px: float = 44.0


class IsoProjector:
    def __init__(self, metrics: IsoMetrics | None = None) -> None:
        self.m = metrics or IsoMetrics()

    def project(self, x: float, y: float, z: float = 0.0) -> QPointF:
        sx = (x - y) * (self.m.tile_width / 2.0)
        sy = (x + y) * (self.m.tile_height / 2.0) - z * self.m.elevation_px
        return QPointF(sx, sy)
