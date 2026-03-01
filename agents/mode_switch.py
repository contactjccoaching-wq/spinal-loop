"""
Spinal Loop — Inhibition Réciproque (Mode Switch)

Deux modes mutuellement exclusifs :
- REFLEX  : réponse directe, Haiku, max 150 tokens
- DELIBERATIVE : chain-of-thought, escalade possible

Un classifier Haiku évalue la requête et verrouille le mode.
Période réfractaire : 3 tours minimum avant re-switch.
"""

from __future__ import annotations
import json
import re
from anthropic import Anthropic

from utils.logger import BioLogger
from utils.context import SharedContext

CLASSIFIER_PROMPT = """Tu es un classifier de requêtes. Ton unique rôle est de déterminer
si une requête nécessite une réponse REFLEXE (rapide, factuelle, simple) ou
DELIBERATIVE (réflexion profonde, analyse, créativité).

REFLEX = questions factuelles simples, salutations, oui/non, calculs basiques,
         définitions courtes, traductions simples.

DELIBERATIVE = analyse, comparaison, création, raisonnement multi-étapes,
               code, rédaction longue, questions ouvertes, stratégie.

Réponds UNIQUEMENT avec ce JSON, rien d'autre :
{"mode": "REFLEX" ou "DELIBERATIVE", "reason": "explication courte"}"""


class ReciprocalInhibitor:
    """Gère le switching exclusif entre modes REFLEX et DELIBERATIVE."""

    def __init__(self, client: Anthropic, config: dict, logger: BioLogger):
        self.client = client
        self.model = config["models"]["level_1"]
        self.refractory_period = config["mode_switch"]["refractory_period"]
        self.logger = logger

    def classify(self, query: str, context: SharedContext) -> str:
        """Classifie la requête → REFLEX ou DELIBERATIVE.

        Respecte le verrouillage et la période réfractaire.
        """
        # Si le mode est verrouillé et la période réfractaire active → garder le mode
        if context.mode and not context.can_switch_mode():
            self.logger.bio_event(
                "SWITCH", model=self.model,
                status="LOCKED",
                remaining=context.refractory_counter
            )
            return context.mode

        response = self.client.messages.create(
            model=self.model,
            max_tokens=100,
            system=CLASSIFIER_PROMPT,
            messages=[{"role": "user", "content": query}]
        )

        self.logger.api_call(
            self.model,
            response.usage.input_tokens,
            response.usage.output_tokens,
            event_type="CLASSIFY"
        )

        text = response.content[0].text.strip()
        mode = self._parse_mode(text)

        # Détecter un switch
        if context.mode and mode != context.mode:
            self.logger.bio_event(
                "SWITCH", model=self.model,
                previous=context.mode, new=mode
            )

        # Verrouiller le mode avec période réfractaire
        context.lock_mode(mode, self.refractory_period)
        context.add_event("SWITCH", {"mode": mode, "query": query[:100]})

        return mode

    def _parse_mode(self, text: str) -> str:
        """Extrait le mode depuis la réponse JSON du classifier."""
        try:
            match = re.search(r'\{[^}]+\}', text)
            if match:
                data = json.loads(match.group())
                mode = data.get("mode", "DELIBERATIVE").upper()
                if mode in ("REFLEX", "DELIBERATIVE"):
                    return mode
        except (json.JSONDecodeError, AttributeError):
            pass
        # Fallback : en cas de doute, mode délibératif
        self.logger.warn("Classification ambiguë → fallback DELIBERATIVE")
        return "DELIBERATIVE"
