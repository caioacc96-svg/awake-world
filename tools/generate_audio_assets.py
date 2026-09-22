from __future__ import annotations

import argparse
import math
import struct
import wave
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIO_DIR = ROOT / "awake_world" / "assets" / "audio"
SAMPLE_RATE = 22_050
MAX_I16 = 32_767


@dataclass(frozen=True)
class AmbientProfile:
    name: str
    frequencies: tuple[float, ...]
    amplitudes: tuple[float, ...]
    pulse_hz: float
    duration: float = 8.0


AMBIENT = (
    AmbientProfile("home_day.wav", (131.0, 196.5, 262.0), (0.020, 0.010, 0.006), 0.25),
    AmbientProfile("home_night.wav", (65.5, 98.25, 131.0), (0.017, 0.009, 0.005), 0.125),
    AmbientProfile("hq_day.wav", (110.0, 165.0, 220.0), (0.028, 0.014, 0.007), 0.25),
    AmbientProfile("hq_night.wav", (82.5, 123.75, 165.0), (0.024, 0.012, 0.006), 0.125),
    AmbientProfile("plaza_day.wav", (153.0, 229.5, 306.0), (0.012, 0.007, 0.004), 0.375),
    AmbientProfile("plaza_night.wav", (98.0, 147.0, 196.0), (0.016, 0.009, 0.005), 0.25),
    AmbientProfile("rooftop_day.wav", (125.0, 187.5, 250.0), (0.011, 0.006, 0.004), 0.25),
    AmbientProfile("rooftop_night.wav", (73.5, 110.25, 147.0), (0.020, 0.010, 0.005), 0.125),
)


def _clamp_i16(value: float) -> int:
    return max(-MAX_I16, min(MAX_I16, int(round(value * MAX_I16))))


def _write_mono(path: Path, samples: list[int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(struct.pack("<" + "h" * len(samples), *samples))


def _ambient(profile: AmbientProfile) -> list[int]:
    total = int(profile.duration * SAMPLE_RATE)
    samples: list[int] = []
    for i in range(total):
        t = i / SAMPLE_RATE
        pulse = 0.84 + 0.16 * math.sin(2.0 * math.pi * profile.pulse_hz * t)
        value = 0.0
        for index, (freq, amp) in enumerate(zip(profile.frequencies, profile.amplitudes)):
            phase = index * math.pi / 3.0
            value += amp * math.sin(2.0 * math.pi * freq * t + phase)
        # Very low deterministic air layer: tonal, periodic and loop-safe.
        value += 0.0025 * math.sin(2.0 * math.pi * 31.25 * t)
        samples.append(_clamp_i16(value * pulse))
    return samples


def _chirp(duration: float, start_hz: float, end_hz: float, amplitude: float) -> list[int]:
    total = int(duration * SAMPLE_RATE)
    samples: list[int] = []
    phase = 0.0
    for i in range(total):
        x = i / max(1, total - 1)
        freq = start_hz + (end_hz - start_hz) * x
        phase += 2.0 * math.pi * freq / SAMPLE_RATE
        attack = min(1.0, x / 0.05)
        release = min(1.0, (1.0 - x) / 0.18)
        env = max(0.0, min(attack, release))
        overtone = 0.28 * math.sin(phase * 2.0)
        samples.append(_clamp_i16(amplitude * env * (math.sin(phase) + overtone)))
    return samples


def generate(force: bool = False) -> list[Path]:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for profile in AMBIENT:
        target = AUDIO_DIR / profile.name
        if force or not target.exists():
            _write_mono(target, _ambient(profile))
            written.append(target)

    cues = {
        "interact.wav": _chirp(0.8, 520.0, 760.0, 0.075),
        "discover.wav": _chirp(1.2, 420.0, 880.0, 0.078),
    }
    for name, samples in cues.items():
        target = AUDIO_DIR / name
        if force or not target.exists():
            _write_mono(target, samples)
            written.append(target)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic Awake World audio assets.")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    written = generate(force=args.force)
    print(f"AWAKE_AUDIO_READY files={len(tuple(AUDIO_DIR.glob('*.wav')))} written={len(written)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
