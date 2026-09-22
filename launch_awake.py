from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
VENV_PYTHON = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def banner(message: str) -> None:
    print(f"[awake/world] {message}", flush=True)


def fail(message: str, code: int = 1) -> int:
    print(f"\n[awake/world] ERROR: {message}", file=sys.stderr, flush=True)
    return code


def run(command: list[str], *, env: dict[str, str] | None = None, quiet: bool = False) -> subprocess.CompletedProcess[str]:
    if quiet:
        return subprocess.run(
            command,
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    return subprocess.run(command, cwd=ROOT, env=env, text=True, check=False)


def ensure_supported_python() -> None:
    if sys.version_info < (3, 11):
        raise RuntimeError(
            f"Python {sys.version_info.major}.{sys.version_info.minor} detected. "
            "Awake World requires Python 3.11 or newer."
        )


def ensure_venv() -> None:
    if VENV_PYTHON.exists():
        probe = run(
            [str(VENV_PYTHON), "-c", "import sys; print(int(sys.version_info >= (3, 11)))"],
            quiet=True,
        )
        if probe.returncode == 0 and probe.stdout.strip() == "1":
            return
        banner("existing .venv is incompatible; rebuilding it...")
        import shutil
        shutil.rmtree(VENV, ignore_errors=True)

    banner("creating isolated Python environment (.venv)...")
    result = run([sys.executable, "-m", "venv", str(VENV)])
    if result.returncode != 0 or not VENV_PYTHON.exists():
        raise RuntimeError("Could not create the local .venv environment.")


def project_env(*, offscreen: bool = False) -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(ROOT) + (os.pathsep + existing if existing else "")
    if offscreen:
        env["QT_QPA_PLATFORM"] = "offscreen"
        env["QT_LOGGING_RULES"] = "qt.multimedia.*=false"
    else:
        env.pop("QT_QPA_PLATFORM", None)
    return env


def ensure_dependencies() -> str:
    banner("checking PySide6 runtime...")
    probe = run(
        [str(VENV_PYTHON), "-c", "import PySide6; print(PySide6.__version__)"],
        env=project_env(),
        quiet=True,
    )
    if probe.returncode == 0:
        return probe.stdout.strip() or "installed"

    banner("PySide6 not found in .venv; installing requirements...")
    install = run(
        [
            str(VENV_PYTHON),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "-r",
            str(ROOT / "requirements.txt"),
        ],
        env=project_env(),
    )
    if install.returncode != 0:
        raise RuntimeError(
            "Dependency installation failed. Check the internet connection and rerun RUN_AWAKE_WORLD.cmd."
        )

    probe = run(
        [str(VENV_PYTHON), "-c", "import PySide6; print(PySide6.__version__)"],
        env=project_env(),
        quiet=True,
    )
    if probe.returncode != 0:
        detail = (probe.stderr or probe.stdout).strip()
        raise RuntimeError(f"PySide6 installation completed but import still failed. {detail}")
    return probe.stdout.strip() or "installed"


def validate() -> None:
    banner("validating project structure...")
    result = run([str(VENV_PYTHON), str(ROOT / "tools" / "static_validate.py")], env=project_env())
    if result.returncode != 0:
        raise RuntimeError("Static validation failed.")


def core_test() -> None:
    banner("running core systems tests...")
    result = run([str(VENV_PYTHON), str(ROOT / "tools" / "core_test.py")], env=project_env())
    if result.returncode != 0:
        raise RuntimeError("Core systems test failed.")


def smoke_test() -> None:
    banner("running offscreen Qt/world smoke test...")
    result = run([str(VENV_PYTHON), str(ROOT / "tools" / "smoke_test.py")], env=project_env(offscreen=True))
    if result.returncode != 0:
        raise RuntimeError("Qt/world smoke test failed. The game was not launched to preserve the original error above.")


def launch() -> int:
    banner("launching Awake World Build 0.4.1 — Living City...")
    result = run([str(VENV_PYTHON), str(ROOT / "run.py")], env=project_env())
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Awake World Build 0.4.1 bootstrap")
    parser.add_argument("--verify-only", action="store_true", help="prepare and validate the build without opening the game")
    parser.add_argument("--no-smoke", action="store_true", help="skip Qt smoke test (diagnostic fallback only)")
    args = parser.parse_args()

    try:
        os.chdir(ROOT)
        ensure_supported_python()
        banner(f"bootstrap Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        ensure_venv()
        version = ensure_dependencies()
        banner(f"PySide6 {version} ready")
        validate()
        core_test()
        if not args.no_smoke:
            smoke_test()
        banner("validation complete")
        if args.verify_only:
            return 0
        return launch()
    except KeyboardInterrupt:
        return fail("Launch cancelled by user.", 130)
    except Exception as exc:
        traceback.print_exc()
        return fail(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
