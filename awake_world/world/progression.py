from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DecorDefinition:
    key: str
    name: str
    description: str
    category: str


DECOR_CATALOG: dict[str, DecorDefinition] = {
    "memory_plant": DecorDefinition(
        "memory_plant", "Memory Plant", "A low ceramic planter that reacts to nearby signals.", "living",
    ),
    "signal_lamp": DecorDefinition(
        "signal_lamp", "Signal Lamp", "A warm floor lamp with a soft Awake pulse.", "light",
    ),
    "woven_rug": DecorDefinition(
        "woven_rug", "Woven Field", "A quiet textile surface for the center of awake/home.", "surface",
    ),
    "record_console": DecorDefinition(
        "record_console", "After-hours Console", "A compact listening console unlocked on the rooftop.", "media",
    ),
    "portal_sculpture": DecorDefinition(
        "portal_sculpture", "Portal Study", "A small sculptural study of the Awake portal geometry.", "object",
    ),
    "garden_stone": DecorDefinition(
        "garden_stone", "Garden Signal Stone", "A mossed signal stone recovered from the commons garden.", "living",
    ),
}

STARTER_DECOR = {"memory_plant", "signal_lamp", "woven_rug"}

JOURNAL_TEXT: dict[str, str] = {
    "arrival": "I arrived before the network was populated. The place still felt inhabited.",
    "mira_intro": "Mira treats the studio like a living instrument: screens wake only when someone needs them.",
    "sol_intro": "Sol keeps the commons kiosk open even when there is no one to serve. Routine seems to matter here.",
    "echo_intro": "Echo says the rooftop is where unfinished signals go when nobody is listening.",
    "signal_triad": "Three dormant signals answered. Their pulse now resolves into a single slow rhythm.",
    "after_hours": "The listening deck changed after dusk. I found an object tagged for awake/home.",
    "home_open": "awake/home is not a menu. It is a room, and the room remembers what I place inside it.",
    "first_rest": "The world keeps moving when I sit still. That may be the point.",
}


def add_journal(state, key: str) -> bool:
    if key in state.journal:
        return False
    state.journal.append(key)
    return True


def unlock_decor(state, key: str) -> bool:
    if key not in DECOR_CATALOG or key in state.inventory:
        return False
    state.inventory.add(key)
    return True


def evaluate_progression(state, room_id: str, phase: str) -> list[str]:
    """Evaluate authored single-player milestones after an interaction or room change."""
    messages: list[str] = []

    awakened_signals = {
        "hq.signal",
        "plaza.garden_signal",
        "roof.sky_signal",
    }
    if awakened_signals.issubset({k for k, v in state.toggles.items() if v}) and "signal_triad" not in state.flags:
        state.flags.add("signal_triad")
        add_journal(state, "signal_triad")
        if unlock_decor(state, "portal_sculpture"):
            messages.append("Network constellation resolved · Portal Study added to your collection")

    if room_id == "rooftop" and phase in {"dusk", "night"} and state.toggles.get("roof.listening_deck"):
        if "after_hours" not in state.flags:
            state.flags.add("after_hours")
            add_journal(state, "after_hours")
            if unlock_decor(state, "record_console"):
                messages.append("After-hours transmission · listening console unlocked for awake/home")

    if room_id == "home" and "home_open" not in state.flags:
        state.flags.add("home_open")
        add_journal(state, "home_open")
        messages.append("awake/home is now persistent · decoration anchors are active")

    return messages


def inventory_lines(state) -> list[str]:
    result = []
    for key in sorted(state.inventory, key=lambda k: DECOR_CATALOG.get(k, DecorDefinition(k, k, "", "")).name):
        definition = DECOR_CATALOG.get(key)
        if definition:
            result.append(f"{definition.name} — {definition.category}")
    return result


def journal_lines(state) -> list[str]:
    return [JOURNAL_TEXT.get(key, key.replace("_", " ").title()) for key in state.journal]
