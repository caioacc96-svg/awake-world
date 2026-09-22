from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("AWAKE_SAVE_DIR", tempfile.mkdtemp(prefix="awake-visual-"))
os.environ.setdefault("QT_LOGGING_RULES", "qt.multimedia.*=false")

SCENES = [
    ("quarter_morning_clear", "quarter", 8*60, "clear"),
    ("quarter_sunset", "quarter", 18*60, "clear"),
    ("quarter_rain", "quarter", 13*60, "rain"),
    ("plaza_night", "central_plaza", 21*60, "clear"),
    ("observatory_sunset", "observatory", 18*60, "clear"),
    ("twin_core_night", "twin_core", 22*60, "clear"),
    ("trinity_lab_daylight", "trinity_lab", 11*60, "clear"),
    ("kawaii_garden_rain", "kawaii_garden", 16*60, "rain"),
    ("pit_night", "pit", 1*60, "clear"),
    ("glasshouse_morning", "glasshouse", 9*60, "clear"),
]


def image_signature(image) -> dict[str, object]:
    # Stable coarse signature: 16x9 luminance buckets + histogram bounds.
    from PySide6.QtCore import QSize
    small = image.scaled(QSize(16, 9))
    values=[]
    for y in range(small.height()):
        for x in range(small.width()):
            c=small.pixelColor(x,y)
            values.append(round((c.red()*0.2126+c.green()*0.7152+c.blue()*0.0722)/255,3))
    raw=json.dumps(values,separators=(",",":")).encode()
    return {"width": image.width(), "height": image.height(), "luma": values, "hash": hashlib.sha256(raw).hexdigest()}


def luma_distance(a: list[float], b: list[float]) -> float:
    if len(a)!=len(b): return 1.0
    return sum(abs(x-y) for x,y in zip(a,b))/max(1,len(a))


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--output", default=str(ROOT/"visual_output"))
    args=parser.parse_args()
    from PySide6.QtCore import QRectF
    from PySide6.QtGui import QImage, QPainter
    from PySide6.QtWidgets import QApplication
    from awake_world.design.theme.engine import ThemeEngine
    from awake_world.world.room import make_room
    from awake_world.world.state import WorldState

    app=QApplication.instance() or QApplication(sys.argv)
    theme=ThemeEngine(); theme.apply(app,"light")
    out=Path(args.output); out.mkdir(parents=True,exist_ok=True)
    baseline_path=ROOT/"visual_baselines"/"signatures.json"
    current={}
    for key,room_id,minute,weather in SCENES:
        state=WorldState(last_room=room_id,world_minutes=minute,weather=weather)
        room=make_room(room_id,theme,state); room.set_world_time(minute,force=True); room.apply_weather(weather); room.advance_ambient(.016)
        rect=room.sceneRect()
        image=QImage(1280,720,QImage.Format.Format_ARGB32); image.fill(0)
        painter=QPainter(image); room.render(painter,QRectF(0,0,1280,720),rect); painter.end()
        image.save(str(out/f"{key}.png"))
        current[key]=image_signature(image)
    candidate_path=out/"signatures.json"
    candidate_path.write_text(json.dumps(current,indent=2,sort_keys=True),encoding="utf-8")
    if args.update:
        baseline_path.parent.mkdir(parents=True,exist_ok=True)
        baseline_path.write_text(json.dumps(current,indent=2,sort_keys=True),encoding="utf-8")
        print(f"AWAKE_VISUAL_BASELINE_UPDATED {baseline_path}")
        return 0
    if not baseline_path.exists():
        print("AWAKE_VISUAL_BASELINE_MISSING")
        return 2
    baseline=json.loads(baseline_path.read_text(encoding="utf-8"))
    failures=[]
    for key,sig in current.items():
        old=baseline.get(key)
        if not old:
            failures.append(f"{key}:missing")
            continue
        if sig["width"]!=old.get("width") or sig["height"]!=old.get("height"):
            failures.append(f"{key}:dimensions")
            continue
        distance=luma_distance(sig["luma"],old.get("luma",[]))
        if distance>0.085:
            failures.append(f"{key}:luma_distance={distance:.4f}")
    if failures:
        print("AWAKE_VISUAL_REGRESSION_FAILED", *failures, sep="\n")
        return 1
    print("AWAKE_VISUAL_REGRESSION_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())