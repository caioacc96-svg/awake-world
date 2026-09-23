from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class IdentityState:
    member_id: str
    display_name: str
    avatar_id: str
    revision: int = 1


@dataclass(frozen=True, slots=True)
class AvatarReplicationState:
    member_id: str
    space_id: str
    x: float
    y: float
    elevation: float
    facing_x: float
    facing_y: float
    motion_state: str
    sequence: int


@dataclass(frozen=True, slots=True)
class InteractionReplicationState:
    member_id: str
    space_id: str
    interaction_id: str
    phase: str
    sequence: int


@dataclass(frozen=True, slots=True)
class SurfaceOccupancyState:
    surface_id: str
    space_id: str
    occupants: tuple[str, ...]
    revision: int


@dataclass(frozen=True, slots=True)
class EphemeralPresenceState:
    member_id: str
    space_id: str
    mode: str
    typing: bool = False
    speaking: bool = False
    camera_active: bool = False
    screen_sharing: bool = False


@dataclass(frozen=True, slots=True)
class MediaReference:
    media_id: str
    kind: str
    locator: str
    owner_id: str
    content_type: str = ""
    title: str = ""


@dataclass(frozen=True, slots=True)
class RealtimeCapabilities:
    voice_ready: bool = True
    video_ready: bool = True
    screen_share_ready: bool = True
    file_reference_ready: bool = True
    media_reference_ready: bool = True
    transport: str = "webrtc_planned"
    authoritative_state: str = "server_future"


@dataclass(slots=True)
class ReplicationEnvelope:
    kind: str
    sequence: int
    payload: dict[str, Any] = field(default_factory=dict)
    schema: int = 1

    @classmethod
    def from_state(cls, kind: str, sequence: int, state: object) -> "ReplicationEnvelope":
        if hasattr(state, "__dataclass_fields__"):
            payload = asdict(state)
        elif isinstance(state, dict):
            payload = dict(state)
        else:
            raise TypeError("replication state must be a dataclass or dict")
        return cls(kind=kind, sequence=max(0, int(sequence)), payload=payload)

    def to_wire(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "kind": self.kind,
            "sequence": self.sequence,
            "payload": self.payload,
        }


def validate_multiplayer_ready_contract() -> tuple[str, ...]:
    capabilities = RealtimeCapabilities()
    failures: list[str] = []
    if not all((
        capabilities.voice_ready,
        capabilities.video_ready,
        capabilities.screen_share_ready,
        capabilities.file_reference_ready,
        capabilities.media_reference_ready,
    )):
        failures.append("capabilities")
    if capabilities.transport != "webrtc_planned":
        failures.append("transport")
    sample = AvatarReplicationState(
        "local_player", "quarter", 1.0, 2.0, .0, .0, 1.0, "idle", 1
    )
    wire = ReplicationEnvelope.from_state("avatar", 1, sample).to_wire()
    if wire["schema"] != 1 or wire["kind"] != "avatar":
        failures.append("envelope")
    return tuple(failures)
