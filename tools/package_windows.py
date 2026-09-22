from __future__ import annotations

import json
from pathlib import Path
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/"dist"/"AWAKE_WORLD.exe"
RELEASE=ROOT/"release"/"AwakeWorld_0.5_GLOBAL_Windows"
ZIP=ROOT/"release"/"AwakeWorld_0.5_GLOBAL_Windows.zip"


def main() -> int:
    if not DIST.exists():
        raise SystemExit("AWAKE_PACKAGE_FAILED: dist/AWAKE_WORLD.exe missing")
    if RELEASE.exists(): shutil.rmtree(RELEASE)
    RELEASE.mkdir(parents=True)
    shutil.copy2(DIST, RELEASE/"AWAKE_WORLD.exe")
    shutil.copytree(ROOT/"awake_world"/"assets", RELEASE/"assets")
    shutil.copytree(ROOT/"data", RELEASE/"data")
    shutil.copytree(ROOT/"licenses", RELEASE/"licenses")
    shutil.copy2(ROOT/"README_START.txt", RELEASE/"README_START.txt")
    build=json.loads((ROOT/"data"/"build.json").read_text(encoding="utf-8"))
    build["artifact"]="AwakeWorld_0.5_GLOBAL_Windows.zip"
    (RELEASE/"data"/"build.json").write_text(json.dumps(build,indent=2,ensure_ascii=False),encoding="utf-8")
    ZIP.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(ZIP,"w",zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(RELEASE.rglob("*")):
            if path.is_file(): zf.write(path,path.relative_to(RELEASE.parent))
    print(ZIP)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
