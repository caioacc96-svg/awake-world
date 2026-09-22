from __future__ import annotations

import math
from dataclasses import dataclass

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsItem

from awake_world.world.iso import IsoProjector
from awake_world.world.items import InteractionSpec


@dataclass(frozen=True)
class NPCProfile:
    key: str
    name: str
    role: str
    accent: str


NPC_PROFILES = {
    "mira": NPCProfile("mira", "Mira", "studio keeper", "#67B99A"),
    "sol": NPCProfile("sol", "Sol", "commons host", "#E9C36A"),
    "echo": NPCProfile("echo", "Echo", "signal gardener", "#9E94D9"),
    "barista": NPCProfile("barista", "Noa", "quarter barista", "#C88F62"),
    "courier": NPCProfile("courier", "Ivo", "courier", "#668FA0"),
    "maintenance": NPCProfile("maintenance", "Nara", "maintenance", "#8A8F70"),
    "momo": NPCProfile("momo", "Momo", "garden dog", "#D89B86"),
}


class NPCItem(QGraphicsItem):
    """Small autonomous resident with a deterministic waypoint routine."""

    def __init__(
        self,
        projector: IsoProjector,
        profile: NPCProfile,
        waypoints: list[tuple[float, float]],
        speed: float = 0.48,
    ) -> None:
        super().__init__()
        self.projector = projector
        self.profile = profile
        self.waypoints = waypoints or [(5.0, 5.0)]
        self.speed = speed
        self.grid_x, self.grid_y = self.waypoints[0]
        self._target_index = 1 % len(self.waypoints)
        self._pause = 0.9
        self._phase = 0.0
        self._facing = QPointF(0.0, 1.0)
        self.behavior_state = "walk"
        self.sync_scene_position()

    def boundingRect(self) -> QRectF:
        return QRectF(-31, -102, 62, 111)

    def paint(self, painter: QPainter, option, widget=None) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        bob = math.sin(self._phase) * 0.9
        accent = QColor(self.profile.accent)
        side = max(-1.0, min(1.0, self._facing.x()))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(18, 20, 28, 34))
        painter.drawEllipse(QRectF(-18, -6, 36, 11))
        painter.save()
        painter.translate(0, bob)

        painter.setBrush(QColor("#353A45"))
        painter.drawRoundedRect(QRectF(-11, -31, 9, 27), 4, 4)
        painter.drawRoundedRect(QRectF(2, -31, 9, 27), 4, 4)
        painter.setBrush(QColor("#F0ECE4"))
        painter.drawRoundedRect(QRectF(-13, -8, 12, 8), 4, 4)
        painter.drawRoundedRect(QRectF(1, -8, 12, 8), 4, 4)

        painter.setBrush(QColor("#262B35"))
        torso = QPainterPath()
        torso.addRoundedRect(QRectF(-18, -63, 36, 36), 11, 11)
        painter.drawPath(torso)
        painter.setBrush(accent)
        painter.drawRoundedRect(QRectF(-10, -59, 20, 27), 7, 7)

        skin = QColor("#C98F6C")
        painter.setBrush(skin)
        painter.drawRoundedRect(QRectF(-4, -69, 8, 9), 4, 4)
        painter.drawEllipse(QRectF(-17, -96, 34, 33))
        painter.setBrush(QColor("#272A31"))
        hair = QPainterPath()
        hair.moveTo(-16, -83)
        hair.cubicTo(-13, -101, 12, -103, 17, -82)
        hair.cubicTo(8, -89, -8, -90, -16, -83)
        painter.drawPath(hair)

        eye_shift = side * 1.1
        painter.setBrush(QColor("#272A31"))
        painter.drawEllipse(QRectF(-8 + eye_shift, -80, 2.5, 2.5))
        painter.drawEllipse(QRectF(5 + eye_shift, -80, 2.5, 2.5))
        painter.setPen(QPen(accent.darker(122), 1.0))
        painter.drawLine(QPointF(-6, -71), QPointF(6, -71))
        painter.restore()

    def set_behavior_state(self, state: str) -> None:
        self.behavior_state = str(state or "idle")
        if self.profile.key == "momo" and self.behavior_state == "seek_shelter":
            self._target_index = 0
            self._pause = 0.0

    def advance_animation(self, dt: float) -> None:
        self._phase += dt * (1.25 if self.behavior_state in {"sleep", "sit", "lunch", "shelter_pause"} else 2.2)
        if not self.isVisible():
            return
        if self.behavior_state in {"sleep", "sit", "lunch", "wipe_counter", "clean", "open_cafe", "serve_shelter_crowd", "maintenance", "inspect", "weather_response", "socialize"}:
            self._pause = max(self._pause, 0.45)
            self.update()
            return
        if len(self.waypoints) <= 1:
            self.update()
            return
        if self._pause > 0:
            self._pause -= dt
            self.update()
            return

        tx, ty = self.waypoints[self._target_index]
        dx, dy = tx - self.grid_x, ty - self.grid_y
        dist = math.hypot(dx, dy)
        if dist < 0.035:
            self.grid_x, self.grid_y = tx, ty
            self._target_index = (self._target_index + 1) % len(self.waypoints)
            self._pause = 1.8 + (self._target_index % 3) * 0.55
        else:
            ux, uy = dx / dist, dy / dist
            step = min(dist, self.speed * dt)
            self.grid_x += ux * step
            self.grid_y += uy * step
            self._facing = QPointF(ux, uy)
        self.sync_scene_position()
        self.update()

    def sync_scene_position(self) -> None:
        p = self.projector.project(self.grid_x, self.grid_y, 0)
        self.setPos(p)
        self.setZValue(p.y() + 880)

    def interaction_spec(self) -> InteractionSpec:
        return InteractionSpec(
            key=f"npc.{self.profile.key}",
            x=self.grid_x,
            y=self.grid_y,
            radius=1.05,
            eyebrow=self.profile.role.upper(),
            title=f"Talk to {self.profile.name}",
            hint="E  talk",
            action="talk",
            target=self.profile.key,
        )
