from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from awake_world.world.systems.events import EventBus, WorldEvent


class PresenceMode(StrEnum):
    AVAILABLE = "available"
    FOCUS = "focus_mode"
    MEETING = "in_meeting"
    AWAY = "away"
    DND = "do_not_disturb"


@dataclass(slots=True)
class PresenceRecord:
    member_id: str
    space_id: str | None = None
    mode: PresenceMode = PresenceMode.AVAILABLE
    party_size: int = 1


class PresenceSystem:
    def __init__(self, bus: EventBus, initial: dict[str, dict[str, object]] | None = None) -> None:
        self.bus = bus
        self.records: dict[str, PresenceRecord] = {}
        self.restore(initial or {})

    def restore(self, data: dict[str, dict[str, object]]) -> None:
        self.records.clear()
        for member_id, raw in data.items():
            try:
                mode = PresenceMode(str(raw.get("mode", PresenceMode.AVAILABLE.value)))
            except ValueError:
                mode = PresenceMode.AVAILABLE
            self.records[str(member_id)] = PresenceRecord(
                member_id=str(member_id),
                space_id=None if raw.get("space_id") is None else str(raw.get("space_id")),
                mode=mode,
                party_size=max(1, int(raw.get("party_size", 1))),
            )

    def set(self, member_id: str, space_id: str | None, mode: PresenceMode = PresenceMode.AVAILABLE, party_size: int = 1) -> None:
        record = PresenceRecord(member_id, space_id, mode, max(1, party_size))
        self.records[member_id] = record
        self.bus.publish(
            WorldEvent.PRESENCE_CHANGED,
            member_id=member_id,
            space_id=space_id,
            mode=mode.value,
            party_size=record.party_size,
        )

    def occupants(self, space_id: str) -> tuple[PresenceRecord, ...]:
        return tuple(r for r in self.records.values() if r.space_id == space_id)

    def snapshot(self) -> dict[str, dict[str, object]]:
        return {
            member_id: {
                "space_id": record.space_id,
                "mode": record.mode.value,
                "party_size": record.party_size,
            }
            for member_id, record in self.records.items()
        }
