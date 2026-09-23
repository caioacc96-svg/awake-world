from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("AWAKE_SAVE_DIR", tempfile.mkdtemp(prefix="awake-cast-"))
os.environ.setdefault("QT_LOGGING_RULES", "qt.multimedia.*=false")


def render_avatar_sheet(target: Path, pose_sheet: bool = False) -> dict[str, object]:
    from PySide6.QtCore import QPointF, QRectF, Qt
    from PySide6.QtGui import QColor, QFont, QImage, QPainter
    from awake_world.world.avatar import AvatarItem
    from awake_world.world.iso import IsoProjector

    image = QImage(1280, 720, QImage.Format.Format_ARGB32)
    image.fill(QColor("#E8E4DB"))
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setFont(QFont("Arial", 12))

    if pose_sheet:
        variants = [
            ("standing", (0, 1), False, False, .0),
            ("walk", (1, 1), True, False, 1.15),
            ("run", (1, 0), True, True, 1.35),
            ("seated", (-1, 1), False, False, .0),
            ("working", (0, -1), False, False, .0),
            ("listening", (-1, 0), False, False, .0),
            ("resting", (1, -1), False, False, .0),
            ("phone", (0, 1), False, False, .0),
        ]
    else:
        variants = [
            ("east", (1, 0), False, False, .0), ("north_east", (1, -1), False, False, .0),
            ("north", (0, -1), False, False, .0), ("north_west", (-1, -1), False, False, .0),
            ("west", (-1, 0), False, False, .0), ("south_west", (-1, 1), False, False, .0),
            ("south", (0, 1), False, False, .0), ("south_east", (1, 1), False, False, .0),
        ]

    positions = [
        QPointF(150, 235), QPointF(450, 235), QPointF(750, 235), QPointF(1050, 235),
        QPointF(150, 565), QPointF(450, 565), QPointF(750, 565), QPointF(1050, 565),
    ]
    for (label, facing, moving, sprinting, phase), pos in zip(variants, positions):
        avatar = AvatarItem(IsoProjector(), QColor("#B99145"))
        avatar.set_facing(*facing)
        if label in {"seated", "working", "listening", "resting", "phone"}:
            avatar.set_pose(label)
        avatar.set_motion_state(moving, sprinting)
        avatar.motion_phase = phase
        painter.save()
        painter.translate(pos)
        painter.scale(1.55, 1.55)
        avatar.paint(painter, None)
        painter.restore()
        painter.setPen(QColor("#30343A"))
        painter.drawText(
            QRectF(pos.x() - 110, pos.y() + 28, 220, 28),
            Qt.AlignmentFlag.AlignHCenter,
            label.replace("_", " "),
        )
    painter.end()
    image.save(str(target))
    return {"width": image.width(), "height": image.height(), "variants": [v[0] for v in variants]}


def render_observatory(target: Path, minute: int, pose: str) -> dict[str, object]:
    from PySide6.QtCore import QRectF
    from PySide6.QtGui import QImage, QPainter
    from PySide6.QtWidgets import QApplication
    from awake_world.design.theme.engine import ThemeEngine
    from awake_world.world.room import make_room
    from awake_world.world.state import WorldState
    from awake_world.world.systems.surfaces import surfaces_for_space

    app = QApplication.instance() or QApplication(sys.argv)
    theme = ThemeEngine()
    theme.apply(app, "light")
    state = WorldState(last_room="observatory", world_minutes=minute, weather="clear")
    room = make_room("observatory", theme, state)
    room.set_world_time(minute, force=True)

    if pose == "working":
        desk = next(s for s in surfaces_for_space("observatory") if s.id == "observatory.desk")
        room.avatar.set_pose("working", desk.x, desk.y, 0.0, -1.0, desk.z)
    elif pose == "listening":
        room.avatar.set_pose("listening", 8.45, 7.15, -1.0, -1.0, room.elevation_at(8.45, 7.15))
    else:
        idle_x, idle_y = 7.25, 7.72
        room.avatar.set_grid_position(idle_x, idle_y, room.elevation_at(idle_x, idle_y))
        room.avatar.set_facing(1.0, -1.0)

    for _ in range(45):
        room.advance_ambient(1 / 30)

    center = room.avatar.scenePos()
    source = QRectF(center.x() - 390, center.y() - 219, 780, 438)
    image = QImage(1280, 720, QImage.Format.Format_ARGB32)
    image.fill(0)
    painter = QPainter(image)
    room.render(painter, QRectF(0, 0, 1280, 720), source)
    painter.end()
    image.save(str(target))
    return {
        "space": "observatory", "minute": minute, "pose": pose,
        "profile": room.avatar.profile_id,
        "grid": [room.avatar.grid_x, room.avatar.grid_y, room.avatar.grid_z],
    }


def main() -> int:
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("awake-world-living-cast-review")

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT / "living_cast_output"))
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    metadata = {
        "direction_sheet": render_avatar_sheet(out / "living_cast_caio_monks_directions.png"),
        "pose_sheet": render_avatar_sheet(out / "living_cast_caio_monks_poses.png", pose_sheet=True),
        "observatory_day": render_observatory(out / "living_cast_observatory_day_idle.png", 11 * 60, "standing"),
        "observatory_dusk_working": render_observatory(out / "living_cast_observatory_dusk_working.png", 18 * 60, "working"),
        "observatory_night_listening": render_observatory(out / "living_cast_observatory_night_listening.png", 22 * 60, "listening"),
    }
    (out / "living_cast_review.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )
    print("AWAKE_LIVING_CAST_RENDER_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
