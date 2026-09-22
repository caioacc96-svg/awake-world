from __future__ import annotations

import os
import sys
import traceback
import tempfile
from pathlib import Path

# Direct execution (python tools\\smoke_test.py) makes tools/ sys.path[0].
# Pin the project root explicitly so awake_world is importable on Windows too.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("AWAKE_SAVE_DIR", tempfile.mkdtemp(prefix="awake-smoke-"))
os.environ.setdefault("QT_LOGGING_RULES", "qt.multimedia.*=false")


def main() -> int:
    try:
        from PySide6.QtWidgets import QApplication

        from awake_world.design.theme.engine import ThemeEngine
        from awake_world.ui.main_window import AwakeMainWindow
        from awake_world.world.room import DISCOVERY_KEYS, ROOM_TYPES, all_room_ids, make_room
        from awake_world.world.save import load_state

        app = QApplication.instance() or QApplication(sys.argv)
        theme = ThemeEngine()
        theme.apply(app, "light")
        state = load_state()

        assert len(DISCOVERY_KEYS) == 29
        assert {"headquarters", "plaza", "rooftop", "home"}.issubset(ROOM_TYPES)

        # Construct every legacy room and Awake Quarter space offscreen.
        for room_id in sorted(all_room_ids()):
            room = make_room(room_id, theme, state)
            room.set_world_time(22 * 60, force=True)
            room.apply_weather("rain")
            room.advance_ambient(0.016)
            room.apply_weather("clear")
            assert room.avatar is not None

        window = AwakeMainWindow(theme)
        window.show()
        app.processEvents()
        window.view.cycle_time_phase()
        app.processEvents()
        window.view._emit_snapshot()
        app.processEvents()
        window.close()
        app.processEvents()
        print("AWAKE_SMOKE_OK")
        return 0
    except Exception:
        print("AWAKE_SMOKE_FAILED")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
