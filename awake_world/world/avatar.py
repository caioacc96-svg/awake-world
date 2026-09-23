from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsItem

from awake_world.design.characters import CharacterProfile, direction_from_vector, get_character_profile
from awake_world.world.iso import IsoProjector


class AvatarItem(QGraphicsItem):
    """Awake 0.7 procedural sprite: modular, directional and elevation-aware."""

    def __init__(
        self,
        projector: IsoProjector,
        accent: QColor,
        profile: CharacterProfile | None = None,
    ) -> None:
        super().__init__()
        self.projector = projector
        self.profile = profile or get_character_profile("caio_monks")
        self.accent = QColor(self.profile.accent if self.profile else accent)
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

    @property
    def profile_id(self) -> str:
        return self.profile.id

    @property
    def direction(self) -> str:
        return direction_from_vector(self.facing.x(), self.facing.y())

    def boundingRect(self) -> QRectF:
        m = self.profile.metrics
        return QRectF(-m.width_px / 2 - 5, -m.height_px + 3, m.width_px + 10, m.height_px + 18)

    @property
    def locked_in_pose(self) -> bool:
        return self.pose != "standing"

    def _q(self, value: str) -> QColor:
        return QColor(value)

    def _direction_traits(self) -> tuple[float, bool, bool]:
        direction = self.direction
        side = 1.0 if "east" in direction else -1.0 if "west" in direction else 0.0
        rear = direction in {"north", "north_east", "north_west"}
        profile_view = direction in {"east", "west"}
        return side, rear, profile_view

    def _draw_shadow(self, painter: QPainter) -> None:
        width = self.profile.metrics.shadow_px * (1.10 if self.sprinting else 1.0)
        alpha = 50 if self.grid_z < .35 else 42
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(14, 18, 23, alpha))
        painter.drawEllipse(QRectF(-width / 2, -7, width, 13))

    def _draw_legs(self, painter: QPainter, stride: float, seated: bool) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._q(self.profile.trousers))
        if seated:
            painter.drawRoundedRect(QRectF(-16, -34, 14, 23), 5, 5)
            painter.drawRoundedRect(QRectF(2, -34, 14, 23), 5, 5)
            painter.setBrush(self._q(self.profile.shoes))
            painter.drawRoundedRect(QRectF(-18, -14, 18, 8), 4, 4)
            painter.drawRoundedRect(QRectF(0, -14, 18, 8), 4, 4)
            return
        painter.drawRoundedRect(QRectF(-13 + stride * .24, -39, 10, 35), 5, 5)
        painter.drawRoundedRect(QRectF(3 - stride * .24, -39, 10, 35), 5, 5)
        painter.setBrush(self._q(self.profile.shoes))
        painter.drawRoundedRect(QRectF(-16 + stride * .31, -9, 15, 9), 4, 4)
        painter.drawRoundedRect(QRectF(1 - stride * .31, -9, 15, 9), 4, 4)

    def _draw_torso(self, painter: QPainter, side: float) -> None:
        jacket = self._q(self.profile.jacket)
        outline = QColor("#15191F")
        outer = QPainterPath()
        outer.addRoundedRect(QRectF(-24 + side * 1.2, -77, 48, 48), 12, 12)
        painter.setPen(QPen(outline, self.profile.metrics.outline_px))
        painter.setBrush(jacket)
        painter.drawPath(outer)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._q(self.profile.shirt))
        painter.drawRoundedRect(QRectF(-10 + side * .5, -70, 20, 34), 7, 7)
        painter.setBrush(self._q(self.profile.accent))
        painter.drawRoundedRect(QRectF(-7 + side * .5, -63, 14, 3), 1.5, 1.5)
        painter.drawRoundedRect(QRectF(-2 + side * .5, -59, 4, 8), 1.5, 1.5)
        painter.setBrush(jacket.lighter(107))
        painter.drawRoundedRect(QRectF(-19 + side, -68, 6, 30), 3, 3)
        painter.drawRoundedRect(QRectF(13 + side, -68, 6, 30), 3, 3)

    def _draw_arms(self, painter: QPainter, stride: float, side: float) -> None:
        jacket = self._q(self.profile.jacket)
        skin = self._q(self.profile.skin)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(jacket)
        arm_swing = stride * .32
        if self.pose == "working":
            painter.drawRoundedRect(QRectF(-26, -65, 9, 30), 4, 4)
            painter.drawRoundedRect(QRectF(17, -65, 9, 30), 4, 4)
            painter.setBrush(skin)
            painter.drawEllipse(QRectF(-20, -39, 8, 8))
            painter.drawEllipse(QRectF(12, -39, 8, 8))
            painter.setBrush(QColor("#D8E0E8"))
            painter.drawRoundedRect(QRectF(-14, -40, 28, 15), 4, 4)
            painter.setBrush(self._q(self.profile.accent).darker(115))
            painter.drawRoundedRect(QRectF(-9, -35, 18, 3), 1.5, 1.5)
        elif self.pose == "phone":
            painter.drawRoundedRect(QRectF(-25, -64, 8, 29), 4, 4)
            painter.drawRoundedRect(QRectF(16, -67, 8, 23), 4, 4)
            painter.setBrush(skin)
            painter.drawEllipse(QRectF(16, -50, 8, 8))
            painter.setBrush(QColor("#11151B"))
            painter.drawRoundedRect(QRectF(17 + side * 2, -60, 7, 14), 2, 2)
        elif self.pose == "listening":
            painter.drawRoundedRect(QRectF(-25, -66, 8, 30), 4, 4)
            painter.drawRoundedRect(QRectF(17, -66, 8, 30), 4, 4)
        elif self.pose == "resting":
            painter.drawRoundedRect(QRectF(-25, -62, 8, 25), 4, 4)
            painter.drawRoundedRect(QRectF(17, -62, 8, 25), 4, 4)
        else:
            painter.drawRoundedRect(QRectF(-28 + arm_swing, -66, 8, 33), 4, 4)
            painter.drawRoundedRect(QRectF(20 - arm_swing, -66, 8, 33), 4, 4)

    def _draw_head(self, painter: QPainter, side: float, rear: bool, profile_view: bool) -> None:
        skin = self._q(self.profile.skin)
        hair = self._q(self.profile.hair)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(skin)
        painter.drawRoundedRect(QRectF(-5 + side, -84, 10, 13), 5, 5)
        painter.drawEllipse(QRectF(-20 + side * 1.5, -114, 40, 39))
        painter.setBrush(hair)
        cap = QPainterPath()
        cap.moveTo(-19 + side, -96)
        cap.cubicTo(-17 + side, -117, 14 + side, -121, 20 + side, -97)
        cap.cubicTo(12 + side, -104, -8 + side, -106, -19 + side, -96)
        painter.drawPath(cap)
        painter.drawRoundedRect(QRectF(-18 + side, -103, 8, 17), 4, 4)

        # Persistent headphones establish the MONKS pilot silhouette.
        painter.setPen(QPen(self._q(self.profile.metal), 2.4))
        painter.drawArc(QRectF(-23 + side, -111, 46, 34), 8 * 16, 164 * 16)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._q(self.profile.accent).darker(110))
        painter.drawRoundedRect(QRectF(-23 + side, -101, 6, 13), 3, 3)
        painter.drawRoundedRect(QRectF(17 + side, -101, 6, 13), 3, 3)

        if rear:
            painter.setBrush(hair.darker(108))
            painter.drawRoundedRect(QRectF(-15 + side, -96, 30, 9), 4, 4)
            return

        painter.setBrush(QColor("#252A31"))
        eye_shift = side * 2.2
        if profile_view:
            painter.drawEllipse(QRectF((-1 if side > 0 else -5) + eye_shift, -94, 3.5, 3.5))
        else:
            painter.drawEllipse(QRectF(-9 + eye_shift, -94, 3.2, 3.2))
            painter.drawEllipse(QRectF(6 + eye_shift, -94, 3.2, 3.2))
        painter.setPen(QPen(skin.darker(120), 1.0))
        painter.drawArc(QRectF(-6 + eye_shift * .4, -86, 12, 7), 205 * 16, 130 * 16)
        painter.setPen(Qt.PenStyle.NoPen)

    def paint(self, painter: QPainter, option, widget=None) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        idle_bob = math.sin(self.idle_phase) * (1.15 if not self.moving and self.pose == "standing" else .28)
        walk_bob = abs(math.sin(self.motion_phase)) * (2.35 if self.moving and self.pose == "standing" else 0.0)
        stride = math.sin(self.motion_phase) * (5.4 if self.moving and self.pose == "standing" else 0.0)
        side, rear, profile_view = self._direction_traits()
        lean = 2.0 if self.sprinting and self.pose == "standing" else 0.0
        seated = self.pose in {"seated", "working", "listening", "resting"}
        y_shift = 11.0 if seated else 0.0

        self._draw_shadow(painter)
        painter.save()
        painter.translate(side * lean, idle_bob - walk_bob + y_shift)
        self._draw_legs(painter, stride, seated)
        self._draw_torso(painter, side)
        self._draw_arms(painter, stride, side)
        self._draw_head(painter, side, rear, profile_view)
        painter.restore()

    def set_profile(self, profile: CharacterProfile) -> None:
        self.prepareGeometryChange()
        self.profile = profile
        self.accent = QColor(profile.accent)
        self.update()

    def set_grid_position(self, x: float, y: float, z: float | None = None) -> None:
        self.grid_x = x
        self.grid_y = y
        if z is not None:
            self.grid_z = float(z)
        self.sync_scene_position()

    def set_facing(self, dx: float, dy: float) -> None:
        if abs(dx) + abs(dy) > .001:
            self.facing = QPointF(dx, dy)
            self.update()

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
        self.update()

    def advance_animation(self, dt: float) -> None:
        self.idle_phase += dt * (2 * math.pi / 3.4)
        if self.moving:
            self.motion_phase += dt * (11.2 if self.sprinting else 7.8)
        else:
            self.motion_phase *= max(0.0, 1.0 - dt * 10.0)
        self.update()

    def sync_scene_position(self) -> None:
        p = self.projector.project(self.grid_x, self.grid_y, self.grid_z)
        self.setPos(p)
        self.setZValue(p.y() + 1000)
