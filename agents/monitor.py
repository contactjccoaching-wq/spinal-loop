"""
Spinal Loop — GTO / Inhibition Autogénique (Moniteur de surcharge)

Analyse l'output de chaque agent et détecte :
- Répétitions excessives
- Longueur anormale
- Incohérence interne
- Saturation / hallucination probable

Si surcharge → inhiber, décomposer en sous-tâches, redistribuer.
"""

from __future__ import annotations
import json
import re
from anthropic import Anthropic

from utils.logger import BioLogger
from utils.context import SharedContext

MONITOR_PROMPT = """Tu es un moniteur de qualité (GTO — Golgi Tendon Organ).
Ton rôle est d'analyser une réponse d'agent et détecter les signes de surcharge.

Analyse la réponse suivante et vérifie ces critères :

1. REPETITIONS : Le même concept est-il répété plus de {max_reps} fois ?
2. LONGUEUR : La réponse fait {actual_len} caractères. Est-ce excessif pour la question posée ?
   (seuil : {max_len} caractères)
3. INCOHERENCE : Y a-t-il des contradictions internes ?
4. SATURATION : La réponse tourne-t-elle en rond ? Y a-t-il des signes d'hallucination ?

Question posée : {query}

Réponse à analyser :
---
{response}
---

Réponds UNIQUEMENT avec ce JSON :
{{
  "overloaded": true/false,
  "signals": {{
    "repetitions": true/false,
    "excessive_length": true/false,
    "incoherence": true/false,
    "saturation": true/false
  }},
  "severity": 0.0 à 1.0,
  "subtasks": ["sous-tâche 1", "sous-tâche 2"] ou [],
  "summary": "description courte du problème ou 'OK'"
}}

Si overloaded=true, propose 2-4 sous-tâches pour décomposer la question originale.
Si overloaded=false, subtasks doit être vide."""


class GTOMonitor:
    """Moniteur de surcharge — détecte et corrige les réponses problématiques."""

    def __init__(self, client: Anthropic, config: dict, logger: BioLogger):
        self.client = client
        self.model = config["models"]["level_1"]  # Haiku pour le monitoring
        self.logger = logger
        self.max_reps = config["gto"]["max_repetitions"]
        self.length_multiplier = config["gto"]["length_multiplier"]
        self.expected_length = config["gto"]["expected_length"]
        self.enabled = config["gto"]["enabled"]

    def analyze(self, query: str, response_text: str,
                context: SharedContext) -> dict:
        """Analyse la réponse pour détecter une surcharge.

        Returns:
            dict avec clés: overloaded, signals, severity, subtasks, summary
        """
        if not self.enabled:
            return {"overloaded": False, "signals": {}, "severity": 0.0,
                    "subtasks": [], "summary": "monitoring disabled"}

        max_len = int(self.expected_length * self.length_multiplier)

        prompt = MONITOR_PROMPT.format(
            max_reps=self.max_reps,
            actual_len=len(response_text),
            max_len=max_len,
            query=query,
            response=response_text[:3000]  # Limiter pour le moniteur
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        self.logger.api_call(
            self.model,
            response.usage.input_tokens,
            response.usage.output_tokens,
            event_type="OVERLOAD"
        )

        result = self._parse_analysis(response.content[0].text)

        if result["overloaded"]:
            self.logger.bio_event(
                "INHIBITION",
                model=self.model,
                severity=result["severity"],
                signals=str(result["signals"]),
                summary=result["summary"]
            )
            context.add_event("INHIBITION", result)

            if result["subtasks"]:
                self.logger.bio_event(
                    "DECOMPOSE",
                    subtasks=len(result["subtasks"])
                )

        return result

    def _parse_analysis(self, text: str) -> dict:
        """Parse la réponse JSON du moniteur."""
        try:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except (json.JSONDecodeError, AttributeError):
            pass

        # Fallback conservateur
        return {
            "overloaded": False,
            "signals": {},
            "severity": 0.0,
            "subtasks": [],
            "summary": "parse error — assuming OK"
        }
