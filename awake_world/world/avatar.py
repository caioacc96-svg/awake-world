from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsItem

from awake_world.world.iso import IsoProjector


class AvatarItem(QGraphicsItem):
    """Authorial vector avatar with locomotion plus contextual single-player poses."""

    def __init__(self, projector: IsoProjector, accent: QColor) -> None:
        super().__init__()
        self.projector = projector
        self.accent = QColor(accent)
        self.grid_x = 5.0
        self.grid_y = 6.5
        self.grid_z = 0.0
        self.motion_phase = 0.0
        self.idle_phase = 0.0
        self.facing = QPointF(0.0, 1.0)
        self.moving = False
        self.sprinting = False
        self.pose = "standing"
        self.sync_scene_position()

    def boundingRect(self) -> QRectF:
        return QRectF(-42, -116, 84, 130)

    @property
    def locked_in_pose(self) -> bool:
        return self.pose != "standing"

    def paint(self, painter: QPainter, option, widget=None) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        idle_bob = math.sin(self.idle_phase) * (1.35 if not self.moving and self.pose == "standing" else 0.35)
        walk_bob = abs(math.sin(self.motion_phase)) * (2.5 if self.moving and self.pose == "standing" else 0.0)
        bob = idle_bob - walk_bob
        stride = math.sin(self.motion_phase) * (5.0 if self.moving and self.pose == "standing" else 0.0)
        lean = 1.6 if self.sprinting and self.pose == "standing" else 0.0
        side_bias = max(-1.0, min(1.0, self.facing.x()))
        seated = self.pose in {"seated", "working", "listening", "resting"}
        y_shift = 10.0 if seated else 0.0

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(18, 20, 28, 40))
        shadow_w = 42 if not self.sprinting else 48
        painter.drawEllipse(QRectF(-shadow_w / 2, -7, shadow_w, 13))

        painter.save()
        painter.translate(side_bias * lean, bob + y_shift)

        painter.setBrush(QColor("#313640"))
        if seated:
            painter.drawRoundedRect(QRectF(-15, -31, 14, 22), 5, 5)
            painter.drawRoundedRect(QRectF(1, -31, 14, 22), 5, 5)
            painter.drawRoundedRect(QRectF(-17, -13, 18, 8), 4, 4)
            painter.drawRoundedRect(QRectF(-1, -13, 18, 8), 4, 4)
        else:
            painter.drawRoundedRect(QRectF(-13 + stride * 0.24, -35, 10, 31), 5, 5)
            painter.drawRoundedRect(QRectF(3 - stride * 0.24, -35, 10, 31), 5, 5)
            painter.setBrush(QColor("#F2EFE7"))
            painter.drawRoundedRect(QRectF(-16 + stride * 0.31, -9, 15, 9), 4, 4)
            painter.drawRoundedRect(QRectF(1 - stride * 0.31, -9, 15, 9), 4, 4)

        painter.setBrush(QColor("#252A34"))
        outer = QPainterPath()
        outer.addRoundedRect(QRectF(-22, -70, 44, 43), 13, 13)
        painter.drawPath(outer)
        painter.setBrush(self.accent)
        inner = QPainterPath()
        inner.addRoundedRect(QRectF(-14, -66, 28, 34), 9, 9)
        painter.drawPath(inner)

        painter.setBrush(QColor("#252A34"))
        arm_swing = stride * 0.34
        if self.pose == "working":
            painter.drawRoundedRect(QRectF(-24, -59, 8, 27), 4, 4)
            painter.drawRoundedRect(QRectF(16, -59, 8, 27), 4, 4)
            painter.setBrush(QColor("#DDE1FF"))
            painter.drawRoundedRect(QRectF(-13, -38, 26, 14), 4, 4)
            painter.setBrush(self.accent.darker(120))
            painter.drawRoundedRect(QRectF(-8, -34, 16, 3), 1.5, 1.5)
        elif self.pose == "listening":
            painter.drawRoundedRect(QRectF(-25, -63, 8, 29), 4, 4)
            painter.drawRoundedRect(QRectF(17, -63, 8, 29), 4, 4)
            painter.setPen(QPen(QColor("#E9C36A"), 2.0))
            painter.drawArc(QRectF(-23, -103, 46, 34), 5 * 16, 170 * 16)
            painter.setPen(Qt.PenStyle.NoPen)
        else:
            painter.drawRoundedRect(QRectF(-27 + arm_swing, -62, 8, 31), 4, 4)
            painter.drawRoundedRect(QRectF(19 - arm_swing, -62, 8, 31), 4, 4)

        skin = QColor("#D7A27E")
        painter.setBrush(skin)
        painter.drawRoundedRect(QRectF(-5, -77, 10, 12), 5, 5)
        painter.drawEllipse(QRectF(-20, -105, 40, 39))

        painter.setBrush(QColor("#2A2D34"))
        hair = QPainterPath()
        hair.moveTo(-19, -88)
        hair.cubicTo(-19, -108, 13, -113, 20, -90)
        hair.cubicTo(13, -98, -8, -99, -19, -88)
        painter.drawPath(hair)

        eye_shift = side_bias * 1.5
        painter.setBrush(QColor("#2C2E35"))
        painter.drawEllipse(QRectF(-9 + eye_shift, -86, 3, 3))
        painter.drawEllipse(QRectF(6 + eye_shift, -86, 3, 3))
        painter.setPen(QPen(QColor("#8A5E4B"), 1.15))
        painter.drawArc(QRectF(-6 + eye_shift * 0.45, -79, 12, 7), 200 * 16, 140 * 16)
        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QColor("#F8F6F0"))
        painter.drawRoundedRect(QRectF(-4, -57, 8, 11), 3, 3)
        painter.setBrush(self.accent.darker(128))
        painter.drawRoundedRect(QRectF(-1.5, -54, 3, 7), 1.5, 1.5)

        painter.restore()

    def set_grid_position(self, x: float, y: float, z: float | None = None) -> None:
        self.grid_x = x
        self.grid_y = y
        if z is not None:
            self.grid_z = float(z)
        self.sync_scene_position()

    def set_facing(self, dx: float, dy: float) -> None:
        if abs(dx) + abs(dy) > 0.001:
            self.facing = QPointF(dx, dy)

    def set_pose(
        self,
        pose: str,
        x: float | None = None,
        y: float | None = None,
        facing_x: float = 0.0,
        facing_y: float = -1.0,
        z: float | None = None,
    ) -> None:
        self.pose = pose
        self.moving = False
        self.sprinting = False
        if x is not None and y is not None:
            self.grid_x = x
            self.grid_y = y
        if z is not None:
            self.grid_z = float(z)
        self.set_facing(facing_x, facing_y)
        self.sync_scene_position()
        self.update()

    def stand(self) -> None:
        if self.pose == "standing":
            return
        self.pose = "standing"
        self.update()

    def set_motion_state(self, moving: bool, sprinting: bool = False) -> None:
        self.moving = moving and self.pose == "standing"
        self.sprinting = sprinting and self.pose == "standing"

    def advance_animation(self, dt: float) -> None:
        self.idle_phase += dt * (2 * math.pi / 3.1)
        if self.moving:
            rate = 10.4 if self.sprinting else 7.4
            self.motion_phase += dt * rate
        else:
            self.motion_phase *= max(0.0, 1.0 - dt * 10.0)
        self.update()

    def sync_scene_position(self) -> None:
        p = self.projector.project(self.grid_x, self.grid_y, self.grid_z)
        self.setPos(p)
        self.setZValue(p.y() + 1000)
