from __future__ import annotations

from dataclasses import dataclass
from math import hypot, sin

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainterPath,
    QPen,
    QPolygonF,
    QRadialGradient,
)
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsItemGroup,
    QGraphicsPathItem,
    QGraphicsPolygonItem,
    QGraphicsRectItem,
    QGraphicsSimpleTextItem,
)

from awake_world.world.iso import IsoProjector


@dataclass(frozen=True)
class InteractionSpec:
    key: str
    x: float
    y: float
    radius: float
    eyebrow: str
    title: str
    hint: str = "E  interact"
    action: str = "inspect"
    target: str | None = None
    anchor_x: float | None = None
    anchor_y: float | None = None
    facing_x: float = 0.0
    facing_y: float = -1.0
    z: float = 0.0
    priority: float = 0.0
    surface_kind: str = ""


@dataclass(frozen=True)
class CollisionRect:
    x: float
    y: float
    w: float
    d: float
    padding: float = 0.12

    def contains(self, px: float, py: float, radius: float = 0.18) -> bool:
        return (
            self.x - self.padding - radius <= px <= self.x + self.w + self.padding + radius
            and self.y - self.padding - radius <= py <= self.y + self.d + self.padding + radius
        )


class IsoFloorTile(QGraphicsPolygonItem):
    def __init__(self, center: QPointF, w: float, h: float, fill: QColor, edge: QColor) -> None:
        poly = QPolygonF([
            QPointF(center.x(), center.y() - h / 2),
            QPointF(center.x() + w / 2, center.y()),
            QPointF(center.x(), center.y() + h / 2),
            QPointF(center.x() - w / 2, center.y()),
        ])
        super().__init__(poly)
        self.setBrush(fill)
        self.setPen(QPen(edge, 0.55))
        self.setZValue(center.y())


class IsoSurfacePatch(QGraphicsPolygonItem):
    """Flat material zone used for rugs, paths and architectural inlays."""

    def __init__(
        self,
        projector: IsoProjector,
        x: float,
        y: float,
        w: float,
        d: float,
        fill: QColor,
        edge: QColor | None = None,
        z: float = 0.012,
        opacity: float = 1.0,
    ) -> None:
        a = projector.project(x, y, z)
        b = projector.project(x + w, y, z)
        c = projector.project(x + w, y + d, z)
        d0 = projector.project(x, y + d, z)
        super().__init__(QPolygonF([a, b, c, d0]))
        self.setBrush(fill)
        self.setPen(QPen(edge, 0.8) if edge else QPen(Qt.PenStyle.NoPen))
        self.setOpacity(opacity)
        self.setZValue(projector.project(x + w, y + d, z).y() + 0.4)


class IsoBlock(QGraphicsItemGroup):
    """Extruded isometric cuboid. `z` allows floating tabletops and architectural layers."""

    def __init__(
        self,
        projector: IsoProjector,
        x: float,
        y: float,
        w: float,
        d: float,
        h: float,
        top: QColor,
        left: QColor,
        right: QColor,
        z: float = 0.0,
        opacity: float = 1.0,
    ) -> None:
        super().__init__()
        p = projector
        a = p.project(x, y, z + h)
        b = p.project(x + w, y, z + h)
        c = p.project(x + w, y + d, z + h)
        d0 = p.project(x, y + d, z + h)
        a0 = p.project(x, y, z)
        b0 = p.project(x + w, y, z)
        c0 = p.project(x + w, y + d, z)
        d1 = p.project(x, y + d, z)

        top_item = QGraphicsPolygonItem(QPolygonF([a, b, c, d0]))
        left_item = QGraphicsPolygonItem(QPolygonF([d0, c, c0, d1]))
        right_item = QGraphicsPolygonItem(QPolygonF([b, c, c0, b0]))
        back_item = QGraphicsPolygonItem(QPolygonF([a, b, b0, a0]))
        for item, color in (
            (back_item, right.darker(104)),
            (left_item, left),
            (right_item, right),
            (top_item, top),
        ):
            item.setBrush(color)
            item.setPen(Qt.PenStyle.NoPen)
            item.setOpacity(opacity)
            self.addToGroup(item)
        self.setZValue(p.project(x + w, y + d, z).y() + 2)


class IsoArchitecturalBlock(QGraphicsItemGroup):
    """Premium low-cost isometric volume with directional material response."""

    def __init__(
        self,
        projector: IsoProjector,
        x: float,
        y: float,
        w: float,
        d: float,
        h: float,
        top: QColor,
        left: QColor,
        right: QColor,
        z: float = 0.0,
        opacity: float = 1.0,
        glass: bool = False,
    ) -> None:
        super().__init__()
        p = projector
        a = p.project(x, y, z + h)
        b = p.project(x + w, y, z + h)
        c = p.project(x + w, y + d, z + h)
        d0 = p.project(x, y + d, z + h)
        a0 = p.project(x, y, z)
        b0 = p.project(x + w, y, z)
        c0 = p.project(x + w, y + d, z)
        d1 = p.project(x, y + d, z)

        def add_face(
            points: list[QPointF],
            base: QColor,
            start: QPointF,
            end: QPointF,
            light: int,
            shade: int,
        ) -> None:
            item = QGraphicsPolygonItem(QPolygonF(points))
            gradient = QLinearGradient(start, end)
            first = QColor(base).lighter(light)
            second = QColor(base).darker(shade)
            if glass:
                first.setAlpha(220)
                second.setAlpha(178)
            gradient.setColorAt(0.0, first)
            gradient.setColorAt(1.0, second)
            item.setBrush(QBrush(gradient))
            edge = QColor(base).darker(120)
            edge.setAlpha(62 if glass else 46)
            item.setPen(QPen(edge, .58))
            item.setOpacity(opacity)
            self.addToGroup(item)

        add_face([a, b, b0, a0], right.darker(103), a, b0, 105, 111)
        add_face([d0, c, c0, d1], left, d0, c0, 104, 110)
        add_face([b, c, c0, b0], right, b, c0, 103, 114)
        add_face([a, b, c, d0], top, a, c, 110, 103)
        self.setZValue(p.project(x + w, y + d, z).y() + 2)


class SoftShadow(QGraphicsEllipseItem):
    def __init__(self, p: QPointF, width: float, height: float, opacity: float = 0.16) -> None:
        super().__init__(-width / 2, -height / 2, width, height)
        self.setPos(p.x(), p.y() + 2)
        self.setBrush(QColor(20, 22, 28))
        self.setPen(Qt.PenStyle.NoPen)
        self.setOpacity(opacity)
        self.setZValue(p.y() - 2)


class PortalDoor(QGraphicsItemGroup):
    def __init__(self, projector: IsoProjector, x: float, y: float, accent: QColor) -> None:
        super().__init__()
        p = projector.project(x, y, 0)
        self.accent = QColor(accent)
        self.phase = 0.0

        glow_gradient = QRadialGradient(0, -39, 55)
        glow_gradient.setColorAt(0.0, QColor(accent.red(), accent.green(), accent.blue(), 86))
        glow_gradient.setColorAt(1.0, QColor(accent.red(), accent.green(), accent.blue(), 0))
        self.glow = QGraphicsEllipseItem(-55, -94, 110, 110)
        self.glow.setBrush(QBrush(glow_gradient))
        self.glow.setPen(Qt.PenStyle.NoPen)

        frame = QGraphicsPathItem()
        path = QPainterPath()
        path.addRoundedRect(QRectF(-34, -94, 68, 94), 20, 20)
        frame.setPath(path)
        frame.setBrush(QColor("#3C424F"))
        frame.setPen(Qt.PenStyle.NoPen)

        inner = QGraphicsPathItem()
        inner_path = QPainterPath()
        inner_path.addRoundedRect(QRectF(-22, -77, 44, 77), 14, 14)
        inner.setPath(inner_path)
        inner.setBrush(QColor("#20242E"))
        inner.setPen(Qt.PenStyle.NoPen)

        self.line = QGraphicsRectItem(-15, -66, 5, 55)
        self.line.setBrush(accent)
        self.line.setPen(Qt.PenStyle.NoPen)

        cap = QGraphicsEllipseItem(-3, -13, 6, 6)
        cap.setBrush(accent.lighter(125))
        cap.setPen(Qt.PenStyle.NoPen)

        for item in (self.glow, frame, inner, self.line, cap):
            self.addToGroup(item)
        self.setPos(p)
        self.setZValue(p.y() + 190)

    def advance_animation(self, dt: float) -> None:
        self.phase += dt * 2.0
        pulse = 0.58 + 0.18 * (0.5 + 0.5 * sin(self.phase))
        self.glow.setOpacity(pulse)


class ArchitecturalPortalDoor(QGraphicsItemGroup):
    """Quiet architectural threshold for authored 0.6 spaces."""

    def __init__(self, projector: IsoProjector, x: float, y: float, accent: QColor) -> None:
        super().__init__()
        p = projector.project(x, y, 0)
        self.accent = QColor(accent)
        self.phase = 0.0

        shadow = QGraphicsEllipseItem(-31, -7, 62, 13)
        shadow.setBrush(QColor(18, 22, 24, 34))
        shadow.setPen(Qt.PenStyle.NoPen)

        glow_gradient = QRadialGradient(0, -43, 46)
        glow_gradient.setColorAt(
            0.0,
            QColor(accent.red(), accent.green(), accent.blue(), 48),
        )
        glow_gradient.setColorAt(
            1.0,
            QColor(accent.red(), accent.green(), accent.blue(), 0),
        )
        self.glow = QGraphicsEllipseItem(-46, -91, 92, 88)
        self.glow.setBrush(QBrush(glow_gradient))
        self.glow.setPen(Qt.PenStyle.NoPen)
        self.glow.setOpacity(.28)

        structure = QColor("#666D72")
        structure_dark = QColor("#4D555A")
        left_post = QGraphicsRectItem(-27, -77, 6, 69)
        right_post = QGraphicsRectItem(21, -77, 6, 69)
        lintel = QGraphicsRectItem(-27, -82, 54, 7)
        threshold = QGraphicsRectItem(-24, -8, 48, 5)
        for item, fill in (
            (left_post, structure),
            (right_post, structure_dark),
            (lintel, structure.lighter(108)),
            (threshold, structure_dark.darker(108)),
        ):
            item.setBrush(fill)
            item.setPen(Qt.PenStyle.NoPen)

        field = QGraphicsRectItem(-20, -73, 40, 61)
        field_fill = QColor(accent)
        field_fill.setAlpha(24)
        field.setBrush(field_fill)
        field_edge = QColor(accent)
        field_edge.setAlpha(46)
        field.setPen(QPen(field_edge, .75))

        self.line = QGraphicsRectItem(-17, -67, 3, 37)
        line_color = QColor(accent).lighter(108)
        line_color.setAlpha(210)
        self.line.setBrush(line_color)
        self.line.setPen(Qt.PenStyle.NoPen)

        marker = QGraphicsEllipseItem(13, -69, 5, 5)
        marker.setBrush(QColor(accent).lighter(126))
        marker.setPen(Qt.PenStyle.NoPen)

        for item in (
            self.glow,
            shadow,
            field,
            left_post,
            right_post,
            lintel,
            threshold,
            self.line,
            marker,
        ):
            self.addToGroup(item)

        self.setPos(p)
        self.setZValue(p.y() + 190)

    def advance_animation(self, dt: float) -> None:
        self.phase += dt * 1.35
        wave = .5 + .5 * sin(self.phase)
        self.glow.setOpacity(.18 + .12 * wave)
        self.line.setOpacity(.72 + .18 * wave)


class PlantItem(QGraphicsItemGroup):
    def __init__(
        self,
        projector: IsoProjector,
        x: float,
        y: float,
        green: QColor,
        scale: float = 1.0,
        motion_phase: float = 0.0,
        motion_amplitude: float = 0.0,
        motion_speed: float = 0.65,
    ) -> None:
        super().__init__()
        p = projector.project(x, y, 0)
        self.origin = QPointF(p)
        self.motion_phase = float(motion_phase)
        self.motion_amplitude = max(0.0, min(2.0, float(motion_amplitude)))
        self.motion_speed = max(0.1, min(1.5, float(motion_speed)))
        shadow = QGraphicsEllipseItem(-18 * scale, -7, 36 * scale, 12)
        shadow.setBrush(QColor(20, 22, 28, 42))
        shadow.setPen(Qt.PenStyle.NoPen)
        pot = QGraphicsEllipseItem(-14 * scale, -15 * scale, 28 * scale, 20 * scale)
        pot.setBrush(QColor("#B98963"))
        pot.setPen(Qt.PenStyle.NoPen)
        rim = QGraphicsEllipseItem(-14 * scale, -17 * scale, 28 * scale, 8 * scale)
        rim.setBrush(QColor("#C99B73"))
        rim.setPen(Qt.PenStyle.NoPen)
        self.addToGroup(shadow)
        self.addToGroup(pot)
        self.addToGroup(rim)
        leaves = [
            (-18, -48, 25, 42, -6),
            (-4, -57, 26, 50, 7),
            (8, -43, 23, 38, 16),
            (-7, -38, 22, 33, -20),
        ]
        for dx, dy, rx, ry, rot in leaves:
            leaf = QGraphicsEllipseItem(dx * scale, dy * scale, rx * scale, ry * scale)
            leaf.setBrush(green.lighter(100 + max(0, rot // 4)))
            leaf.setPen(Qt.PenStyle.NoPen)
            leaf.setRotation(rot)
            self.addToGroup(leaf)
        self.setPos(p)
        self.setZValue(p.y() + 42 * scale)

    def advance_animation(self, dt: float) -> None:
        if self.motion_amplitude <= 0.0:
            return
        self.motion_phase += max(0.0, dt) * self.motion_speed
        self.setPos(
            self.origin.x() + sin(self.motion_phase) * self.motion_amplitude,
            self.origin.y() + sin(self.motion_phase * .73) * self.motion_amplitude * .28,
        )


class ScreenItem(QGraphicsItemGroup):
    def __init__(self, projector: IsoProjector, x: float, y: float, accent: QColor, scale: float = 1.0) -> None:
        super().__init__()
        p = projector.project(x, y, 0)
        self.accent = QColor(accent)
        self.phase = 0.0
        self.active = False

        glow_gradient = QRadialGradient(0, -49 * scale, 52 * scale)
        glow_gradient.setColorAt(0.0, QColor(accent.red(), accent.green(), accent.blue(), 68))
        glow_gradient.setColorAt(1.0, QColor(accent.red(), accent.green(), accent.blue(), 0))
        self.glow = QGraphicsEllipseItem(-52 * scale, -96 * scale, 104 * scale, 90 * scale)
        self.glow.setBrush(QBrush(glow_gradient))
        self.glow.setPen(Qt.PenStyle.NoPen)

        frame = QGraphicsPathItem()
        path = QPainterPath()
        path.addRoundedRect(QRectF(-37 * scale, -76 * scale, 74 * scale, 49 * scale), 7, 7)
        frame.setPath(path)
        frame.setBrush(QColor("#343A46"))
        frame.setPen(Qt.PenStyle.NoPen)

        self.display = QGraphicsPathItem()
        dpath = QPainterPath()
        dpath.addRoundedRect(QRectF(-31 * scale, -70 * scale, 62 * scale, 37 * scale), 4, 4)
        self.display.setPath(dpath)
        self.display.setPen(Qt.PenStyle.NoPen)

        self.line_a = QGraphicsRectItem(-23 * scale, -60 * scale, 30 * scale, 3 * scale)
        self.line_b = QGraphicsRectItem(-23 * scale, -52 * scale, 43 * scale, 3 * scale)
        self.line_c = QGraphicsRectItem(-23 * scale, -44 * scale, 21 * scale, 3 * scale)
        for line in (self.line_a, self.line_b, self.line_c):
            line.setPen(Qt.PenStyle.NoPen)

        stem = QGraphicsRectItem(-4 * scale, -28 * scale, 8 * scale, 20 * scale)
        stem.setBrush(QColor("#4C5361"))
        stem.setPen(Qt.PenStyle.NoPen)
        foot = QGraphicsRectItem(-18 * scale, -10 * scale, 36 * scale, 6 * scale)
        foot.setBrush(QColor("#4C5361"))
        foot.setPen(Qt.PenStyle.NoPen)

        for item in (self.glow, frame, self.display, self.line_a, self.line_b, self.line_c, stem, foot):
            self.addToGroup(item)
        self.setPos(p)
        self.setZValue(p.y() + 150)
        self.set_active(False)

    def set_active(self, active: bool) -> None:
        self.active = active
        if active:
            grad = QLinearGradient(0, -70, 0, -33)
            grad.setColorAt(0, self.accent.lighter(150))
            grad.setColorAt(1, self.accent.lighter(108))
            self.display.setBrush(QBrush(grad))
            for line in (self.line_a, self.line_b, self.line_c):
                line.setBrush(QColor(255, 255, 255, 160))
            self.glow.setOpacity(0.72)
        else:
            self.display.setBrush(self.accent.lighter(172))
            for line in (self.line_a, self.line_b, self.line_c):
                line.setBrush(QColor(255, 255, 255, 75))
            self.glow.setOpacity(0.10)

    def advance_animation(self, dt: float) -> None:
        if not self.active:
            return
        self.phase += dt * 2.5
        self.glow.setOpacity(0.58 + 0.12 * (0.5 + 0.5 * sin(self.phase)))


class BeaconItem(QGraphicsItemGroup):
    def __init__(self, projector: IsoProjector, x: float, y: float, accent: QColor, tall: bool = False) -> None:
        super().__init__()
        p = projector.project(x, y, 0)
        self.accent = QColor(accent)
        self.phase = 0.0
        self.active = False
        stem_h = 48 if tall else 34

        base = QGraphicsEllipseItem(-16, -9, 32, 16)
        base.setBrush(QColor("#48505D"))
        base.setPen(Qt.PenStyle.NoPen)
        rim = QGraphicsEllipseItem(-11, -7, 22, 10)
        rim.setBrush(QColor("#636C7A"))
        rim.setPen(Qt.PenStyle.NoPen)
        stem = QGraphicsRectItem(-3, -stem_h - 7, 6, stem_h)
        stem.setBrush(QColor("#606978"))
        stem.setPen(Qt.PenStyle.NoPen)

        gradient = QRadialGradient(0, -stem_h - 17, 30)
        gradient.setColorAt(0.0, QColor(accent.red(), accent.green(), accent.blue(), 210))
        gradient.setColorAt(1.0, QColor(accent.red(), accent.green(), accent.blue(), 0))
        self.halo = QGraphicsEllipseItem(-30, -stem_h - 47, 60, 60)
        self.halo.setBrush(QBrush(gradient))
        self.halo.setPen(Qt.PenStyle.NoPen)
        self.glow = QGraphicsEllipseItem(-10, -stem_h - 27, 20, 20)
        self.glow.setPen(Qt.PenStyle.NoPen)

        for item in (self.halo, base, rim, stem, self.glow):
            self.addToGroup(item)
        self.setPos(p)
        self.setZValue(p.y() + 110)
        self.set_active(False)

    def set_active(self, active: bool) -> None:
        self.active = active
        self.glow.setBrush(self.accent.lighter(108 if active else 180))
        self.glow.setOpacity(1.0 if active else 0.45)
        self.halo.setOpacity(0.72 if active else 0.12)

    def advance_animation(self, dt: float) -> None:
        self.phase += dt * (2.8 if self.active else 1.1)
        base = 0.55 if self.active else 0.08
        amp = 0.18 if self.active else 0.04
        self.halo.setOpacity(base + amp * (0.5 + 0.5 * sin(self.phase)))


class FloorLampItem(QGraphicsItemGroup):
    def __init__(self, projector: IsoProjector, x: float, y: float, accent: QColor) -> None:
        super().__init__()
        p = projector.project(x, y, 0)
        self.accent = QColor(accent)
        self.active = False
        self.phase = 0.0

        base = QGraphicsEllipseItem(-14, -7, 28, 11)
        base.setBrush(QColor("#555C68"))
        base.setPen(Qt.PenStyle.NoPen)
        stem = QGraphicsRectItem(-2, -78, 4, 72)
        stem.setBrush(QColor("#666E7A"))
        stem.setPen(Qt.PenStyle.NoPen)
        shade_path = QPainterPath()
        shade_path.moveTo(-17, -78)
        shade_path.lineTo(17, -78)
        shade_path.lineTo(11, -58)
        shade_path.lineTo(-11, -58)
        shade_path.closeSubpath()
        shade = QGraphicsPathItem(shade_path)
        shade.setBrush(QColor("#E3D2AE"))
        shade.setPen(Qt.PenStyle.NoPen)

        gradient = QRadialGradient(0, -65, 55)
        gradient.setColorAt(0.0, QColor(accent.red(), accent.green(), accent.blue(), 160))
        gradient.setColorAt(1.0, QColor(accent.red(), accent.green(), accent.blue(), 0))
        self.halo = QGraphicsEllipseItem(-55, -120, 110, 110)
        self.halo.setBrush(QBrush(gradient))
        self.halo.setPen(Qt.PenStyle.NoPen)
        for item in (self.halo, base, stem, shade):
            self.addToGroup(item)
        self.setPos(p)
        self.setZValue(p.y() + 135)
        self.set_active(False)

    def set_active(self, active: bool) -> None:
        self.active = active
        self.halo.setOpacity(0.62 if active else 0.05)

    def advance_animation(self, dt: float) -> None:
        if not self.active:
            return
        self.phase += dt * 1.6
        self.halo.setOpacity(0.52 + 0.10 * (0.5 + 0.5 * sin(self.phase)))


class WallArtItem(QGraphicsItemGroup):
    def __init__(self, projector: IsoProjector, x: float, y: float, z: float, accent: QColor, variant: int = 0) -> None:
        super().__init__()
        p = projector.project(x, y, z)
        shadow = QGraphicsRectItem(-30, -36, 60, 42)
        shadow.setBrush(QColor(20, 22, 28, 35))
        shadow.setPen(Qt.PenStyle.NoPen)
        shadow.setPos(3, 4)
        frame = QGraphicsRectItem(-30, -36, 60, 42)
        frame.setBrush(QColor("#F5F0E6"))
        frame.setPen(QPen(QColor("#B7B0A4"), 2))
        motif = QGraphicsPathItem()
        path = QPainterPath()
        if variant % 2 == 0:
            path.moveTo(-18, -10)
            path.cubicTo(-6, -31, 6, 0, 19, -23)
        else:
            path.moveTo(-18, -27)
            path.lineTo(15, -13)
            path.lineTo(-5, -4)
        motif.setPath(path)
        motif.setPen(QPen(accent, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        for item in (shadow, frame, motif):
            self.addToGroup(item)
        self.setPos(p)
        self.setZValue(p.y() + 130)


class ShelfItem(QGraphicsItemGroup):
    def __init__(self, projector: IsoProjector, x: float, y: float, accent: QColor) -> None:
        super().__init__()
        p = projector.project(x, y, 0)
        back = QGraphicsRectItem(-34, -83, 68, 78)
        back.setBrush(QColor("#665648"))
        back.setPen(Qt.PenStyle.NoPen)
        self.addToGroup(back)
        for y0 in (-65, -43, -21):
            shelf = QGraphicsRectItem(-31, y0, 62, 4)
            shelf.setBrush(QColor("#B18B65"))
            shelf.setPen(Qt.PenStyle.NoPen)
            self.addToGroup(shelf)
        colors = [accent, QColor("#D78769"), QColor("#6AA98A"), QColor("#D5B756"), QColor("#7E83B8")]
        positions = [(-25, -78, 7, 13), (-16, -75, 6, 10), (-7, -79, 8, 14), (4, -76, 6, 11), (14, -80, 9, 15)]
        for i, (bx, by, bw, bh) in enumerate(positions):
            book = QGraphicsRectItem(bx, by, bw, bh)
            book.setBrush(colors[i % len(colors)])
            book.setPen(Qt.PenStyle.NoPen)
            self.addToGroup(book)
        self.setPos(p)
        self.setZValue(p.y() + 145)


class ZoneLabel(QGraphicsSimpleTextItem):
    def __init__(self, text: str, p: QPointF, color: QColor) -> None:
        super().__init__(text.upper())
        self.setBrush(color)
        f = self.font()
        f.setPointSizeF(7.7)
        f.setBold(True)
        f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.45)
        self.setFont(f)
        self.setOpacity(0.46)
        self.setPos(p.x() - self.boundingRect().width() / 2, p.y())
        self.setZValue(p.y() + 1)


class InteractionAnchorItem(QGraphicsItemGroup):
    """Small world-space acknowledgement; never becomes a HUD prompt."""

    def __init__(self, projector: IsoProjector, x: float, y: float, z: float, accent: QColor) -> None:
        super().__init__()
        p = projector.project(x, y, z + .018)
        self.accent = QColor(accent)
        self.ring = QGraphicsEllipseItem(-13, -6, 26, 12)
        fill = QColor(accent)
        fill.setAlpha(16)
        edge = QColor(accent)
        edge.setAlpha(58)
        self.ring.setBrush(fill)
        self.ring.setPen(QPen(edge, .9))
        self.dot = QGraphicsEllipseItem(-2.2, -2.2, 4.4, 4.4)
        self.dot.setBrush(QColor(accent.red(), accent.green(), accent.blue(), 92))
        self.dot.setPen(Qt.PenStyle.NoPen)
        self.addToGroup(self.ring)
        self.addToGroup(self.dot)
        self.setPos(p)
        self.setOpacity(.34)
        self.setZValue(p.y() + 6)

    def set_active(self, active: bool) -> None:
        self.setOpacity(.86 if active else .34)
        self.setScale(1.08 if active else 1.0)


def nearest_interaction(interactions: list[InteractionSpec], x: float, y: float) -> InteractionSpec | None:
    best: tuple[float, InteractionSpec] | None = None
    for item in interactions:
        dist = hypot(x - item.x, y - item.y)
        if dist <= item.radius and (best is None or dist < best[0]):
            best = (dist, item)
    return best[1] if best else None


class DecorAnchorItem(QGraphicsItemGroup):
    """Subtle physical socket for awake/home decoration placement."""

    def __init__(self, projector: IsoProjector, x: float, y: float, accent: QColor, occupied: bool = False) -> None:
        super().__init__()
        p = projector.project(x, y, 0.018)
        ring = QGraphicsEllipseItem(-21, -10, 42, 20)
        ring.setBrush(QColor(accent.red(), accent.green(), accent.blue(), 22 if occupied else 10))
        ring.setPen(QPen(QColor(accent.red(), accent.green(), accent.blue(), 95 if occupied else 62), 1.2, Qt.PenStyle.DashLine))
        dot = QGraphicsEllipseItem(-3, -3, 6, 6)
        dot.setBrush(QColor(accent.red(), accent.green(), accent.blue(), 130 if occupied else 80))
        dot.setPen(Qt.PenStyle.NoPen)
        self.addToGroup(ring)
        self.addToGroup(dot)
        self.setPos(p)
        self.setOpacity(0.9 if occupied else 0.55)
        self.setZValue(p.y() + 2)


class DecorItem(QGraphicsItemGroup):
    """Small authored decor primitives used by awake/home anchors."""

    def __init__(self, projector: IsoProjector, x: float, y: float, key: str, accent: QColor) -> None:
        super().__init__()
        p = projector.project(x, y, 0)
        self.key = key

        shadow = QGraphicsEllipseItem(-18, -7, 36, 12)
        shadow.setBrush(QColor(20, 22, 28, 35))
        shadow.setPen(Qt.PenStyle.NoPen)
        self.addToGroup(shadow)

        if key == "memory_plant":
            pot = QGraphicsEllipseItem(-12, -18, 24, 18)
            pot.setBrush(QColor("#A8785E")); pot.setPen(Qt.PenStyle.NoPen)
            self.addToGroup(pot)
            for dx, dy, w, h, rot in [(-15,-48,22,36,-14),(-2,-57,24,45,8),(7,-44,20,34,18)]:
                leaf = QGraphicsEllipseItem(dx, dy, w, h)
                leaf.setBrush(QColor("#688F72")); leaf.setPen(Qt.PenStyle.NoPen); leaf.setRotation(rot)
                self.addToGroup(leaf)
        elif key == "signal_lamp":
            base = QGraphicsEllipseItem(-13, -7, 26, 10); base.setBrush(QColor("#555C68")); base.setPen(Qt.PenStyle.NoPen)
            stem = QGraphicsRectItem(-2, -60, 4, 54); stem.setBrush(QColor("#666E7A")); stem.setPen(Qt.PenStyle.NoPen)
            shade = QGraphicsEllipseItem(-16, -68, 32, 18); shade.setBrush(QColor("#E3D2AE")); shade.setPen(Qt.PenStyle.NoPen)
            glow = QGraphicsEllipseItem(-27, -78, 54, 54); glow.setBrush(QColor(accent.red(), accent.green(), accent.blue(), 48)); glow.setPen(Qt.PenStyle.NoPen)
            for item in (glow, base, stem, shade): self.addToGroup(item)
        elif key == "woven_rug":
            rug = QGraphicsEllipseItem(-36, -15, 72, 30); rug.setBrush(QColor("#B8A594")); rug.setPen(QPen(QColor("#9D8978"), 1.2))
            line = QGraphicsRectItem(-22, -2, 44, 3); line.setBrush(QColor("#D9C9B8")); line.setPen(Qt.PenStyle.NoPen)
            self.addToGroup(rug); self.addToGroup(line)
        elif key == "record_console":
            body = QGraphicsRectItem(-28, -40, 56, 34); body.setBrush(QColor("#303641")); body.setPen(Qt.PenStyle.NoPen)
            deck = QGraphicsEllipseItem(-17, -34, 34, 14); deck.setBrush(QColor("#141821")); deck.setPen(Qt.PenStyle.NoPen)
            label = QGraphicsRectItem(-11, -17, 22, 5); label.setBrush(accent); label.setPen(Qt.PenStyle.NoPen)
            leg_a = QGraphicsRectItem(-22, -8, 4, 8); leg_b = QGraphicsRectItem(18, -8, 4, 8)
            for leg in (leg_a, leg_b): leg.setBrush(QColor("#4B5260")); leg.setPen(Qt.PenStyle.NoPen)
            for item in (body, deck, label, leg_a, leg_b): self.addToGroup(item)
        elif key == "portal_sculpture":
            outer = QGraphicsPathItem(); path = QPainterPath(); path.addRoundedRect(QRectF(-19, -48, 38, 48), 11, 11)
            outer.setPath(path); outer.setBrush(QColor("#3C424F")); outer.setPen(Qt.PenStyle.NoPen)
            inner = QGraphicsPathItem(); ip = QPainterPath(); ip.addRoundedRect(QRectF(-10, -36, 20, 36), 7, 7)
            inner.setPath(ip); inner.setBrush(QColor("#20242E")); inner.setPen(Qt.PenStyle.NoPen)
            slash = QGraphicsRectItem(-6, -29, 4, 22); slash.setBrush(accent); slash.setPen(Qt.PenStyle.NoPen)
            for item in (outer, inner, slash): self.addToGroup(item)
        elif key == "garden_stone":
            stone = QGraphicsEllipseItem(-22, -25, 44, 28); stone.setBrush(QColor("#626B62")); stone.setPen(Qt.PenStyle.NoPen)
            moss = QGraphicsEllipseItem(-15, -28, 27, 14); moss.setBrush(QColor("#688F72")); moss.setPen(Qt.PenStyle.NoPen)
            mark = QGraphicsEllipseItem(-4, -16, 8, 8); mark.setBrush(accent); mark.setPen(Qt.PenStyle.NoPen)
            for item in (stone,moss,mark): self.addToGroup(item)
        else:
            cube = QGraphicsRectItem(-16,-28,32,28); cube.setBrush(accent.darker(115)); cube.setPen(Qt.PenStyle.NoPen); self.addToGroup(cube)

        self.setPos(p)
        self.setZValue(p.y() + 118)


class SlidingDoorItem(QGraphicsItemGroup):
    """A compact animated door used by lift/home transitions."""

    def __init__(self, projector: IsoProjector, x: float, y: float, accent: QColor) -> None:
        super().__init__()
        p = projector.project(x, y, 0)
        self.progress = 0.0
        self.target = 0.0
        frame = QGraphicsRectItem(-32, -88, 64, 88)
        frame.setBrush(QColor("#3B424E")); frame.setPen(Qt.PenStyle.NoPen)
        self.left = QGraphicsRectItem(-25, -78, 24, 78)
        self.right = QGraphicsRectItem(1, -78, 24, 78)
        for panel in (self.left, self.right):
            panel.setBrush(QColor("#53616C")); panel.setPen(Qt.PenStyle.NoPen)
        mark = QGraphicsRectItem(-3, -58, 6, 28); mark.setBrush(accent); mark.setPen(Qt.PenStyle.NoPen)
        for item in (frame, self.left, self.right, mark): self.addToGroup(item)
        self.setPos(p)
        self.setZValue(p.y()+180)

    def set_open(self, open_: bool) -> None:
        self.target = 1.0 if open_ else 0.0

    def advance_animation(self, dt: float) -> None:
        if abs(self.progress - self.target) < 0.001:
            return
        speed = 4.5 * dt
        if self.progress < self.target:
            self.progress = min(self.target, self.progress + speed)
        else:
            self.progress = max(self.target, self.progress - speed)
        travel = 20 * self.progress
        self.left.setPos(-travel, 0)
        self.right.setPos(travel, 0)


class AmbientMoteItem(QGraphicsEllipseItem):
    def __init__(self, p: QPointF, accent: QColor, phase: float = 0.0, radius: float = 2.0) -> None:
        super().__init__(-radius, -radius, radius*2, radius*2)
        self.origin = QPointF(p)
        self.phase = phase
        self.radius = radius
        self.setBrush(QColor(accent.red(), accent.green(), accent.blue(), 115))
        self.setPen(Qt.PenStyle.NoPen)
        self.setPos(self.origin)
        self.setOpacity(0.34)
        self.setZValue(p.y() + 45)

    def advance_animation(self, dt: float) -> None:
        self.phase += dt * (0.65 + self.radius * 0.08)
        self.setPos(
            self.origin.x() + sin(self.phase * 0.77) * (8 + self.radius * 2),
            self.origin.y() + sin(self.phase) * 7,
        )
        self.setOpacity(0.20 + 0.18 * (0.5 + 0.5 * sin(self.phase * 1.37)))
