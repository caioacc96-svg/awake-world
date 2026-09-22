from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True, slots=True)
class CameraProfile:
    damping: float = 10.0
    dead_zone: float = 8.0
    look_ahead_seconds: float = 0.12
    look_ahead_limit: float = 44.0
    zoom: float = 1.02
    zoom_damping: float = 8.0


@dataclass(slots=True)
class CameraState:
    x: float = 0.0
    y: float = 0.0
    zoom: float = 1.0
    initialized: bool = False


CAMERA_PROFILES: dict[str, CameraProfile] = {
    "outdoor": CameraProfile(damping=10.5, dead_zone=10.0, look_ahead_seconds=0.14, look_ahead_limit=52.0, zoom=0.98),
    "plaza": CameraProfile(damping=10.0, dead_zone=11.0, look_ahead_seconds=0.16, look_ahead_limit=58.0, zoom=0.96),
    "indoor": CameraProfile(damping=12.0, dead_zone=6.0, look_ahead_seconds=0.08, look_ahead_limit=30.0, zoom=1.05),
    "rooftop": CameraProfile(damping=9.0, dead_zone=9.0, look_ahead_seconds=0.12, look_ahead_limit=45.0, zoom=0.94),
    "social": CameraProfile(damping=11.0, dead_zone=7.0, look_ahead_seconds=0.10, look_ahead_limit=34.0, zoom=1.02),
}


class CameraController:
    def __init__(self) -> None:
        self.state = CameraState()

    def snap(self, x: float, y: float, zoom: float = 1.0) -> CameraState:
        self.state = CameraState(float(x), float(y), float(zoom), True)
        return self.state

    def update(
        self,
        dt: float,
        target_x: float,
        target_y: float,
        velocity_x: float,
        velocity_y: float,
        profile: CameraProfile,
    ) -> CameraState:
        if not self.state.initialized:
            return self.snap(target_x, target_y, profile.zoom)

        speed = math.hypot(velocity_x, velocity_y)
        if speed > 1e-6:
            scale = min(profile.look_ahead_limit, speed * profile.look_ahead_seconds)
            target_x += velocity_x / speed * scale
            target_y += velocity_y / speed * scale

        dx = target_x - self.state.x
        dy = target_y - self.state.y
        distance = math.hypot(dx, dy)
        if distance <= profile.dead_zone:
            target_x = self.state.x
            target_y = self.state.y
        elif distance > 1e-6:
            remaining = distance - profile.dead_zone
            target_x = self.state.x + dx / distance * remaining
            target_y = self.state.y + dy / distance * remaining

        follow = 1.0 - math.exp(-profile.damping * max(0.0, dt))
        zoom_follow = 1.0 - math.exp(-profile.zoom_damping * max(0.0, dt))
        self.state.x += (target_x - self.state.x) * follow
        self.state.y += (target_y - self.state.y) * follow
        self.state.zoom += (profile.zoom - self.state.zoom) * zoom_follow
        return self.state
