from __future__ import annotations

import argparse
import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from awake_world.design.theme.engine import ThemeEngine
from awake_world.ui.main_window import AwakeMainWindow


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--smoke-test", action="store_true")
    args, _ = parser.parse_known_args(sys.argv[1:])

    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setApplicationName("awake/world")
    app.setOrganizationName("Awake")
    app.setFont(QFont("Inter", 10))

    theme = ThemeEngine()
    theme.apply(app, "light")
    window = AwakeMainWindow(theme)
    window.show()

    if args.smoke_test:
        def finish() -> None:
            window.view._emit_snapshot()
            window.close()
            app.quit()
        QTimer.singleShot(350, finish)
    return app.exec()
