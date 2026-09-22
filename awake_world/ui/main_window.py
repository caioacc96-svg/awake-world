from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from awake_world.design.theme.engine import ThemeEngine
from awake_world.ui.portal_mark import PortalMark
from awake_world.world.items import InteractionSpec
from awake_world.world.view import GameView


class AwakeMainWindow(QMainWindow):
    def __init__(self, theme: ThemeEngine) -> None:
        super().__init__()
        self.theme = theme
        self.night_shell = False
        self._snapshot: dict = {}
        self.setWindowTitle("awake/world — The Living Network")
        self.resize(1460, 920)
        self.setMinimumSize(1100, 720)

        root = QWidget()
        root.setObjectName("Root")
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self._build_topbar())

        self.stage = QWidget()
        self.stage.setObjectName("Stage")
        stage_layout = QVBoxLayout(self.stage)
        stage_layout.setContentsMargins(0, 0, 0, 0)
        stage_layout.setSpacing(0)

        self.view = GameView(theme)
        self.view.interactionChanged.connect(self._on_interaction_changed)
        self.view.worldMessage.connect(self._on_world_message)
        self.view.roomChanged.connect(self._on_room_changed)
        self.view.explorationChanged.connect(self._on_exploration_changed)
        self.view.timeChanged.connect(self._on_time_changed)
        self.view.snapshotChanged.connect(self._on_snapshot_changed)
        self.view.panelRequested.connect(self._on_panel_requested)
        stage_layout.addWidget(self.view, 1)

        self.action_card = self._build_action_card(self.stage)
        self.action_card.hide()
        self.field_panel = self._build_field_panel(self.stage)
        self.field_panel.hide()
        self.debug_panel = self._build_debug_panel(self.stage)
        self.debug_panel.hide()
        outer.addWidget(self.stage, 1)

        footer = QWidget()
        footer.setObjectName("Footer")
        footer.setFixedHeight(28)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(18, 0, 18, 0)
        footer_layout.setSpacing(10)
        self._status = QLabel("Build 0.5 GLOBAL · cloud validation")
        self._status.setObjectName("BuildLabel")
        footer_layout.addWidget(self._status, 1)
        self._exploration = QLabel("discoveries 0/29")
        self._exploration.setObjectName("BuildLabel")
        self._exploration.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        footer_layout.addWidget(self._exploration)
        outer.addWidget(footer)

        self.view.setFocus()

    def _build_topbar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("TopBar")
        bar.setFixedHeight(62)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 18, 0)
        layout.setSpacing(11)

        layout.addWidget(PortalMark(self.theme.color("awake_blue")))
        brand_col = QVBoxLayout()
        brand_col.setSpacing(0)
        brand = QLabel("awake/world")
        brand.setObjectName("BrandLabel")
        self.room_label = QLabel("awake/headquarters · living studio")
        self.room_label.setObjectName("RoomLabel")
        brand_col.addWidget(brand)
        brand_col.addWidget(self.room_label)
        layout.addLayout(brand_col)
        layout.addStretch(1)

        self.status_pill = QLabel("●  solo")
        self.status_pill.setObjectName("StatusPill")
        layout.addWidget(self.status_pill)

        self.time_button = QPushButton("08:24")
        self.time_button.setObjectName("TimeButton")
        self.time_button.setToolTip("Cycle world light · shortcut T")
        self.time_button.clicked.connect(self._cycle_time)
        layout.addWidget(self.time_button)

        notes_btn = QPushButton("Notes")
        notes_btn.setObjectName("HelpButton")
        notes_btn.setToolTip("Field notes · shortcut I")
        notes_btn.clicked.connect(self._toggle_field_notes)
        layout.addWidget(notes_btn)

        help_btn = QPushButton("Controls")
        help_btn.setObjectName("HelpButton")
        help_btn.clicked.connect(self._show_controls)
        layout.addWidget(help_btn)
        return bar

    def _build_action_card(self, parent: QWidget) -> QFrame:
        card = QFrame(parent)
        card.setObjectName("ActionCard")
        card.setFixedSize(276, 82)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(1)
        self.action_eyebrow = QLabel("OBJECT")
        self.action_eyebrow.setObjectName("ActionEyebrow")
        self.action_title = QLabel("Interaction")
        self.action_title.setObjectName("ActionTitle")
        self.action_hint = QLabel("E  interact")
        self.action_hint.setObjectName("ActionHint")
        layout.addWidget(self.action_eyebrow)
        layout.addWidget(self.action_title)
        layout.addWidget(self.action_hint)
        self.action_opacity = QGraphicsOpacityEffect(card)
        self.action_opacity.setOpacity(1.0)
        card.setGraphicsEffect(self.action_opacity)
        card.raise_()
        return card

    def _build_field_panel(self, parent: QWidget) -> QFrame:
        panel = QFrame(parent)
        panel.setObjectName("FieldPanel")
        panel.setFixedWidth(340)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        top = QHBoxLayout()
        title = QLabel("FIELD NOTES")
        title.setObjectName("PanelTitle")
        top.addWidget(title)
        top.addStretch(1)
        close = QPushButton("×")
        close.setObjectName("PanelClose")
        close.setFixedSize(28, 28)
        close.clicked.connect(self._toggle_field_notes)
        top.addWidget(close)
        layout.addLayout(top)

        self.panel_meta = QLabel("single-player state")
        self.panel_meta.setObjectName("PanelMeta")
        layout.addWidget(self.panel_meta)

        scroll = QScrollArea()
        scroll.setObjectName("PanelScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        body = QWidget()
        body.setObjectName("PanelBody")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 4, 0)
        body_layout.setSpacing(8)

        carry = QLabel("CARRY")
        carry.setObjectName("PanelSection")
        body_layout.addWidget(carry)
        self.inventory_text = QLabel("No objects yet.")
        self.inventory_text.setObjectName("PanelText")
        self.inventory_text.setWordWrap(True)
        body_layout.addWidget(self.inventory_text)

        journal = QLabel("JOURNAL")
        journal.setObjectName("PanelSection")
        body_layout.addWidget(journal)
        self.journal_text = QLabel("The world has not left a note yet.")
        self.journal_text.setObjectName("PanelText")
        self.journal_text.setWordWrap(True)
        body_layout.addWidget(self.journal_text)
        body_layout.addStretch(1)

        scroll.setWidget(body)
        layout.addWidget(scroll, 1)

        hint = QLabel("I  close · decor is placed physically inside awake/home")
        hint.setObjectName("PanelHint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.panel_opacity = QGraphicsOpacityEffect(panel)
        self.panel_opacity.setOpacity(1.0)
        panel.setGraphicsEffect(self.panel_opacity)
        panel.raise_()
        return panel

    def _build_debug_panel(self, parent: QWidget) -> QFrame:
        panel = QFrame(parent)
        panel.setObjectName("FieldPanel")
        panel.setFixedWidth(430)
        root = QVBoxLayout(panel); root.setContentsMargins(16,16,16,16); root.setSpacing(9)
        title = QLabel("WORLD DEBUG · F3"); title.setObjectName("PanelTitle"); root.addWidget(title)
        self.debug_meta = QLabel("runtime ready"); self.debug_meta.setObjectName("PanelMeta"); root.addWidget(self.debug_meta)

        def section(name: str, entries: list[tuple[str, object]]) -> None:
            label=QLabel(name); label.setObjectName("PanelSection"); root.addWidget(label)
            grid=QGridLayout(); grid.setSpacing(6)
            for i,(text,callback) in enumerate(entries):
                btn=QPushButton(text); btn.setObjectName("HelpButton"); btn.clicked.connect(callback); grid.addWidget(btn,i//4,i%4)
            root.addLayout(grid)

        section("SIMULATION", [("PAUSE/RUN",self.view.toggle_simulation_pause),("1 TICK",self.view.single_simulation_tick),("0.25×",lambda:self.view.set_simulation_speed(.25)),("1×",lambda:self.view.set_simulation_speed(1.0)),("4×",lambda:self.view.set_simulation_speed(4.0)),("EXPORT DIAG",self.view.export_diagnostics)])
        section("TIME", [("06:00",lambda:self.view.jump_to_time(360)),("12:00",lambda:self.view.jump_to_time(720)),("18:00",lambda:self.view.jump_to_time(1080)),("00:00",lambda:self.view.jump_to_time(0))])
        section("WEATHER", [("CLEAR",lambda:self.view.set_weather("clear")),("CLOUDY",lambda:self.view.set_weather("cloudy")),("RAIN",lambda:self.view.set_weather("rain"))])
        section("EVENT", [("DELIVERY",lambda:self.view.trigger_microevent("delivery")),("BLACKOUT",lambda:self.view.trigger_microevent("power_flicker")),("DOG",lambda:self.view.trigger_microevent("dog_in_plaza")),("ROOFTOP",lambda:self.view.trigger_microevent("rooftop_session"))])
        section("TELEPORT", [("QUARTER",lambda:self.view.teleport("quarter")),("OBSERVATORY",lambda:self.view.teleport("observatory")),("TWIN CORE",lambda:self.view.teleport("twin_core")),("TRINITY",lambda:self.view.teleport("trinity_lab")),("PIT",lambda:self.view.teleport("pit")),("GARDEN",lambda:self.view.teleport("kawaii_garden")),("PLAZA",lambda:self.view.teleport("central_plaza")),("GLASS",lambda:self.view.teleport("glasshouse"))])
        detail_title=QLabel("INSPECTOR"); detail_title.setObjectName("PanelSection"); root.addWidget(detail_title)
        self.debug_detail=QLabel("player · waiting for snapshot"); self.debug_detail.setObjectName("PanelText"); self.debug_detail.setWordWrap(True); root.addWidget(self.debug_detail)
        root.addStretch(1)
        hint=QLabel("F3 close · debug controls mutate the real world state"); hint.setObjectName("PanelHint"); root.addWidget(hint)
        return panel

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._reposition_action_card()
        self._reposition_field_panel()
        self._reposition_debug_panel()

    def _reposition_action_card(self) -> None:
        if not hasattr(self, "action_card"):
            return
        x = (self.stage.width() - self.action_card.width()) // 2
        y = self.stage.height() - self.action_card.height() - 22
        self.action_card.move(x, y)

    def _reposition_field_panel(self) -> None:
        if not hasattr(self, "field_panel"):
            return
        h = max(430, self.stage.height() - 36)
        self.field_panel.setFixedHeight(h)
        self.field_panel.move(self.stage.width() - self.field_panel.width() - 18, 18)

    def _reposition_debug_panel(self) -> None:
        if not hasattr(self, "debug_panel"):
            return
        self.debug_panel.setFixedHeight(max(500, self.stage.height()-36))
        self.debug_panel.move(18,18)
        self.debug_panel.raise_()

    def _fade_in(self, widget: QWidget, effect: QGraphicsOpacityEffect) -> None:
        effect.setOpacity(0.0)
        widget.show()
        widget.raise_()
        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(int(self.theme.value("motion_normal_ms", 175)))
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _on_interaction_changed(self, spec: InteractionSpec | None) -> None:
        if spec is None:
            self.action_card.hide()
            return
        self.action_eyebrow.setText(spec.eyebrow)
        self.action_title.setText(spec.title)
        self.action_hint.setText(spec.hint)
        self._reposition_action_card()
        self._fade_in(self.action_card, self.action_opacity)

    def _on_world_message(self, message: str) -> None:
        self._status.setText(message)

    def _on_room_changed(self, room_label: str) -> None:
        self.room_label.setText(room_label)
        self._status.setText(f"Entered {room_label.split(' · ')[0]}")

    def _on_exploration_changed(self, current: int, total: int) -> None:
        self._exploration.setText(f"discoveries {current}/{total}")
        if current == total:
            self._status.setText("Current world pass complete · every authored interaction has been found")

    def _on_time_changed(self, time_label: str, phase: str) -> None:
        self.time_button.setText(time_label)
        should_night_shell = phase == "night"
        if should_night_shell != self.night_shell:
            self.night_shell = should_night_shell
            app = QApplication.instance()
            if app is not None:
                self.theme.apply(app, "night" if should_night_shell else "light")

    def _on_snapshot_changed(self, snapshot: object) -> None:
        if not isinstance(snapshot, dict):
            return
        self._snapshot = snapshot
        inventory = snapshot.get("inventory", [])
        journal = snapshot.get("journal", [])
        self.inventory_text.setText("\n".join(f"• {line}" for line in inventory) if inventory else "No objects yet.")
        self.journal_text.setText("\n\n".join(str(line) for line in journal) if journal else "The world has not left a note yet.")
        audio_label = "ambient audio active" if snapshot.get("audio") else "ambient audio unavailable · silent fallback"
        self.panel_meta.setText(
            f"{snapshot.get('discoveries', 0)}/{snapshot.get('discovery_total', 0)} authored discoveries · {audio_label}"
        )
        if hasattr(self, "debug_meta"):
            events = ", ".join(snapshot.get("active_events", [])) or "none"
            paused = "PAUSED" if snapshot.get("simulation_paused") else f"{snapshot.get('simulation_speed',1):g}×"
            self.debug_meta.setText(f"tick {snapshot.get('simulation_tick',0)} · {paused} · weather {snapshot.get('weather', 'clear')} · NPC {snapshot.get('active_npcs',0)} · events {events}")
        if hasattr(self, "debug_detail"):
            player=snapshot.get("player", {}) if isinstance(snapshot.get("player"), dict) else {}
            camera=snapshot.get("camera", {}) if isinstance(snapshot.get("camera"), dict) else {}
            npcs=snapshot.get("npc_states", {}) if isinstance(snapshot.get("npc_states"), dict) else {}
            npc_line="; ".join(f"{k}:{v.get('state','?')}@{v.get('space_id','?')}[{v.get('simulation_lod','?')}]" for k,v in list(npcs.items())[:4] if isinstance(v,dict))
            self.debug_detail.setText(
                f"PLAYER\npos {player.get('position')}  vel {player.get('velocity')}\nstate {player.get('state')}  target {getattr(self.view._last_interaction,'key',None)}\n"
                f"CAMERA\n({camera.get('x')}, {camera.get('y')}) zoom {camera.get('zoom')}\n"
                f"NPC\n{npc_line or 'none'}"
            )

    def _on_panel_requested(self, panel: str) -> None:
        if panel == "field_notes":
            self._toggle_field_notes()
        elif panel == "world_debug":
            self._toggle_debug_panel()

    def _toggle_debug_panel(self) -> None:
        if self.debug_panel.isVisible():
            self.debug_panel.hide()
        else:
            self._reposition_debug_panel(); self.debug_panel.show(); self.debug_panel.raise_()
        self.view.setFocus()

    def _toggle_field_notes(self) -> None:
        if self.field_panel.isVisible():
            self.field_panel.hide()
        else:
            self._reposition_field_panel()
            self._fade_in(self.field_panel, self.panel_opacity)
        self.view.setFocus()

    def _cycle_time(self) -> None:
        self.view.cycle_time_phase()
        self.view.setFocus()

    def _show_controls(self) -> None:
        self._status.setText("WASD/arrows move · Shift run · E interact/use/sit · I field notes · F3 world debug · wheel zoom · T cycle world light")
        self.view.setFocus()
