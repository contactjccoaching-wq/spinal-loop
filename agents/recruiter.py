"""
Spinal Loop — Principe de Henneman (Recrutement ordonné)

Trois niveaux d'agents ordonnés par puissance croissante :
  Niveau 1 : Haiku (réflexe rapide)
  Niveau 2 : Sonnet (intermédiaire)
  Niveau 3 : Opus (délibératif profond)

Règle : toujours commencer par Haiku. Escalader si confiance < seuil
OU complexité > seuil. Ne jamais sauter de niveau.
"""

from __future__ import annotations
import json
import re
from anthropic import Anthropic

from utils.logger import BioLogger
from utils.context import SharedContext

AGENT_SYSTEM_PROMPT = """Tu es un agent de niveau {level} dans un système multi-agents.

Réponds à la question de l'utilisateur de manière complète et précise.

{context_from_previous}

IMPORTANT — À la fin de ta réponse, tu DOIS inclure un bloc d'auto-évaluation
dans exactement ce format (sur une ligne séparée) :

<evaluation>
{{"confidence": X.X, "complexity": X.X, "escalate": true/false, "reason": "..."}}
</evaluation>

Règles d'évaluation :
- confidence (0.0 à 1.0) : à quel point tu es sûr de ta réponse
  - 1.0 = certain, factuel, simple
  - 0.5 = incertain, partiel
  - 0.0 = ne sait pas du tout
- complexity (0.0 à 1.0) : complexité perçue de la tâche
  - 0.0 = trivial
  - 0.5 = modéré
  - 1.0 = extrêmement complexe, multi-domaines
- escalate : true si tu penses qu'un agent plus puissant ferait mieux
- reason : justification courte

Ne mentionne PAS le système multi-agents dans ta réponse à l'utilisateur.
Le bloc <evaluation> sera retiré avant d'afficher la réponse."""

REFLEX_SYSTEM_PROMPT = """Tu es un agent réflexe ultra-rapide.
Réponds de manière directe, concise, factuelle. Pas de chain-of-thought.
Maximum 2-3 phrases courtes."""


class HennemanRecruiter:
    """Implémente le recrutement ordonné par coût (Principe de Henneman)."""

    def __init__(self, client: Anthropic, config: dict, logger: BioLogger):
        self.client = client
        self.logger = logger
        self.levels = [
            config["models"]["level_1"],
            config["models"]["level_2"],
            config["models"]["level_3"],
        ]
        self.confidence_threshold = config["henneman"]["confidence_threshold"]
        self.complexity_threshold = config["henneman"]["complexity_threshold"]

    def process_reflex(self, query: str, context: SharedContext,
                       max_tokens: int = 150) -> str:
        """Mode REFLEX — Haiku uniquement, réponse directe."""
        model = self.levels[0]
        self.logger.bio_event("REFLEX", model=model)

        messages = context.get_messages_for_api()
        messages.append({"role": "user", "content": query})

        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=REFLEX_SYSTEM_PROMPT,
            messages=messages
        )

        self.logger.api_call(
            model,
            response.usage.input_tokens,
            response.usage.output_tokens,
            event_type="REFLEX"
        )

        return response.content[0].text.strip()

    def process(self, query: str, context: SharedContext) -> tuple[str, dict]:
        """Mode DELIBERATIVE — recrutement ordonné avec escalade possible.

        Returns:
            (response_text, evaluation_dict)
        """
        previous_context = ""

        for level_idx, model in enumerate(self.levels):
            level_num = level_idx + 1
            self.logger.bio_event(
                "RECRUIT", model=model, level=level_num
            )

            system = AGENT_SYSTEM_PROMPT.format(
                level=level_num,
                context_from_previous=previous_context
            )

            messages = context.get_messages_for_api()
            messages.append({"role": "user", "content": query})

            response = self.client.messages.create(
                model=model,
                max_tokens=4096,
                system=system,
                messages=messages
            )

            self.logger.api_call(
                model,
                response.usage.input_tokens,
                response.usage.output_tokens,
                event_type="RECRUIT"
            )

            raw_text = response.content[0].text.strip()
            clean_text, evaluation = self._parse_response(raw_text)

            # Décision d'escalade
            if self._should_escalate(evaluation) and level_idx < len(self.levels) - 1:
                self.logger.bio_event(
                    "ESCALADE",
                    model=model,
                    confidence=evaluation.get("confidence", "?"),
                    complexity=evaluation.get("complexity", "?"),
                    reason=evaluation.get("reason", "unknown")
                )
                context.add_event("ESCALADE", {
                    "from_level": level_num,
                    "to_level": level_num + 1,
                    "evaluation": evaluation
                })
                # Passer le contexte de la réponse précédente au niveau supérieur
                previous_context = (
                    f"L'agent de niveau {level_num} a fourni cette réponse "
                    f"(confiance: {evaluation.get('confidence', '?')}) :\n"
                    f"---\n{clean_text}\n---\n"
                    f"Améliore ou complète cette réponse si nécessaire."
                )
                continue

            # Pas d'escalade → réponse finale
            return clean_text, evaluation

        # Si on arrive ici, on est au dernier niveau (ne devrait pas arriver normalement)
        return clean_text, evaluation

    def _parse_response(self, text: str) -> tuple[str, dict]:
        """Sépare la réponse utilisateur du bloc d'évaluation."""
        evaluation = {}
        clean_text = text

        match = re.search(
            r'<evaluation>\s*(\{.*?\})\s*</evaluation>',
            text, re.DOTALL
        )
        if match:
            try:
                evaluation = json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
            clean_text = text[:match.start()].rstrip()

        # Fallback : chercher un JSON brut en fin de texte
        if not evaluation:
            match2 = re.search(
                r'\{[^{]*"confidence"[^}]*\}',
                text, re.DOTALL
            )
            if match2:
                try:
                    evaluation = json.loads(match2.group())
                    clean_text = text[:match2.start()].rstrip()
                except json.JSONDecodeError:
                    pass

        # Si rien trouvé, defaults conservateurs → pas d'escalade par défaut
        if not evaluation:
            evaluation = {
                "confidence": 0.8,
                "complexity": 0.3,
                "escalate": False,
                "reason": "evaluation block not found"
            }

        return clean_text, evaluation

    def _should_escalate(self, evaluation: dict) -> bool:
        """Détermine si l'escalade est nécessaire."""
        if evaluation.get("escalate", False):
            return True
        confidence = evaluation.get("confidence", 1.0)
        complexity = evaluation.get("complexity", 0.0)
        return (confidence < self.confidence_threshold or
                complexity > self.complexity_threshold)
