"""
Spinal Loop — Contexte partagé

Maintient l'état global de la session :
- Historique de conversation
- Mode actif (REFLEX / DELIBERATIVE)
- Phase (EXPLORATION / CONSOLIDATION)
- Compteur de tours et période réfractaire
- Journal des événements biologiques
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal
from datetime import datetime


@dataclass
class BioEvent:
    """Un événement biologique loggé."""
    timestamp: str
    event_type: str
    details: dict


@dataclass
class SharedContext:
    """État global partagé entre tous les composants."""

    # Mode et phase
    mode: Literal["REFLEX", "DELIBERATIVE"] | None = None
    phase: Literal["EXPLORATION", "CONSOLIDATION"] = "EXPLORATION"

    # Compteurs
    turn_count: int = 0
    refractory_counter: int = 0

    # Historique
    conversation: list[dict] = field(default_factory=list)
    events: list[BioEvent] = field(default_factory=list)

    # Verrouillage
    mode_locked: bool = False

    def add_user_message(self, content: str):
        self.conversation.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str):
        self.conversation.append({"role": "assistant", "content": content})

    def add_event(self, event_type: str, details: dict | None = None):
        self.events.append(BioEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            details=details or {}
        ))

    def increment_turn(self):
        self.turn_count += 1
        if self.refractory_counter > 0:
            self.refractory_counter -= 1

    def lock_mode(self, mode: str, refractory_period: int):
        self.mode = mode
        self.mode_locked = True
        self.refractory_counter = refractory_period

    def can_switch_mode(self) -> bool:
        return self.refractory_counter <= 0

    def switch_phase(self, new_phase: str):
        self.phase = new_phase
        self.add_event("REVERSAL", {"new_phase": new_phase})

    def get_messages_for_api(self, last_n: int | None = None) -> list[dict]:
        """Retourne l'historique au format API Anthropic."""
        msgs = self.conversation
        if last_n:
            msgs = msgs[-last_n:]
        return [{"role": m["role"], "content": m["content"]} for m in msgs]
