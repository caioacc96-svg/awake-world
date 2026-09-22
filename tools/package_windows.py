from __future__ import annotations

import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "AWAKE_WORLD.exe"


def artifact_stem(version: str) -> str:
    clean = version.removesuffix("-dev").replace(".", "_")
    channel = "DEV" if version.endswith("-dev") else "GLOBAL"
    return f"AwakeWorld_{clean}_{channel}_Windows"


def main() -> int:
    if not DIST.exists():
        raise SystemExit("AWAKE_PACKAGE_FAILED: dist/AWAKE_WORLD.exe missing")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    stem = artifact_stem(version)
    release_dir = ROOT / "release" / stem
    zip_path = ROOT / "release" / f"{stem}.zip"

    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir(parents=True)
    shutil.copy2(DIST, release_dir / "AWAKE_WORLD.exe")
    shutil.copytree(ROOT / "awake_world" / "assets", release_dir / "assets")
    shutil.copytree(ROOT / "data", release_dir / "data")
    shutil.copytree(ROOT / "licenses", release_dir / "licenses")
    shutil.copy2(ROOT / "README_START.txt", release_dir / "README_START.txt")

    build = json.loads((ROOT / "data" / "build.json").read_text(encoding="utf-8"))
    build["artifact"] = zip_path.name
    (release_dir / "data" / "build.json").write_text(
        json.dumps(build, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(release_dir.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(release_dir.parent))
    print(zip_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
