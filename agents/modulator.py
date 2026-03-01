"""
Spinal Loop — Reflex Reversal (Modulateur à polarité contextuelle)

Un agent dont le comportement s'inverse selon la phase :

- EXPLORATION : amplifie les idées divergentes, challenge les hypothèses
- CONSOLIDATION : inhibe la divergence, force la convergence, structure

La phase est détectée automatiquement (tour N) ou par keyword.
"""

from __future__ import annotations
from anthropic import Anthropic

from utils.logger import BioLogger
from utils.context import SharedContext

EXPLORATION_PROMPT = """Tu es un modulateur en phase EXPLORATION.

Ton rôle : AMPLIFIER la pensée divergente.

Étant donné la réponse ci-dessous, enrichis-la en :
- Ajoutant des connexions inattendues entre domaines
- Posant des questions provocantes qui challengent les hypothèses
- Suggérant des angles alternatifs non explorés
- Introduisant des analogies surprenantes

Ne reformule PAS la réponse. Ajoute un bloc "Perspectives" à la fin
avec 2-4 pistes divergentes courtes. Garde la réponse originale intacte.

Réponse originale :
---
{response}
---"""

CONSOLIDATION_PROMPT = """Tu es un modulateur en phase CONSOLIDATION.

Ton rôle : INHIBER la divergence et FORCER la convergence.

Étant donné la réponse ci-dessous, restructure-la en :
- Éliminant toute redondance
- Fusionnant les idées similaires
- Structurant en points actionnables numérotés
- Ajoutant une conclusion de synthèse de 2 phrases max

Ne garde que l'essentiel. Sois brutal dans l'élagage.

Réponse originale :
---
{response}
---"""


class ReflexModulator:
    """Modulateur à polarité contextuelle — EXPLORATION ou CONSOLIDATION."""

    def __init__(self, client: Anthropic, config: dict, logger: BioLogger):
        self.client = client
        self.model = config["models"]["level_1"]  # Haiku pour la modulation
        self.logger = logger
        self.phase_switch_turn = config["modulator"]["phase_switch_turn"]
        self.consolidation_keywords = config["modulator"]["consolidation_keywords"]

    def detect_phase(self, query: str, context: SharedContext) -> str:
        """Détecte la phase automatiquement ou par keyword."""
        query_lower = query.lower().strip()

        # Détection par keyword (prioritaire)
        for keyword in self.consolidation_keywords:
            if keyword in query_lower:
                if context.phase != "CONSOLIDATION":
                    context.switch_phase("CONSOLIDATION")
                    self.logger.bio_event(
                        "REVERSAL",
                        trigger="keyword",
                        keyword=keyword,
                        phase="CONSOLIDATION"
                    )
                return "CONSOLIDATION"

        # Détection par tour
        if context.turn_count >= self.phase_switch_turn:
            if context.phase != "CONSOLIDATION":
                context.switch_phase("CONSOLIDATION")
                self.logger.bio_event(
                    "REVERSAL",
                    trigger="turn_count",
                    turn=context.turn_count,
                    phase="CONSOLIDATION"
                )
            return "CONSOLIDATION"

        return context.phase

    def modulate(self, response_text: str, query: str,
                 context: SharedContext) -> str:
        """Applique la modulation selon la phase active."""
        phase = self.detect_phase(query, context)

        if phase == "EXPLORATION":
            prompt = EXPLORATION_PROMPT.format(response=response_text)
        else:
            prompt = CONSOLIDATION_PROMPT.format(response=response_text)

        self.logger.bio_event(
            "MODULATE", model=self.model, phase=phase
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        self.logger.api_call(
            self.model,
            response.usage.input_tokens,
            response.usage.output_tokens,
            event_type="MODULATE"
        )

        return response.content[0].text.strip()
