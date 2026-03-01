"""
Spinal Loop Orchestrator — Logique principale

Coordonne les 4 mécanismes biologiques :
1. Henneman (recrutement ordonné)
2. GTO (moniteur de surcharge)
3. Inhibition réciproque (mode switch)
4. Reflex reversal (modulation contextuelle)
"""

from __future__ import annotations
import yaml
from pathlib import Path
from anthropic import Anthropic

__version__ = "1.0.0"

from utils.logger import BioLogger
from utils.context import SharedContext
from agents.mode_switch import ReciprocalInhibitor
from agents.recruiter import HennemanRecruiter
from agents.monitor import GTOMonitor
from agents.modulator import ReflexModulator


class SpinalLoopOrchestrator:
    """Orchestrateur principal du système Spinal Loop."""

    def __init__(self, config_path: str | None = None):
        # Charger la config
        if config_path is None:
            config_path = str(Path(__file__).parent / "config.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        # Client Anthropic (lit ANTHROPIC_API_KEY depuis l'environnement)
        self.client = Anthropic()

        # Logger
        log_cfg = self.config.get("logging", {})
        self.logger = BioLogger(
            log_file=log_cfg.get("file", "spinal_loop.log"),
            level=log_cfg.get("level", "INFO")
        )

        # Contexte partagé
        self.context = SharedContext()

        # Composants biologiques
        self.mode_switch = ReciprocalInhibitor(self.client, self.config, self.logger)
        self.recruiter = HennemanRecruiter(self.client, self.config, self.logger)
        self.monitor = GTOMonitor(self.client, self.config, self.logger)
        self.modulator = ReflexModulator(self.client, self.config, self.logger)

    def process(self, query: str) -> str:
        """Traite une requête utilisateur à travers le pipeline complet.

        Flow :
        1. Incrémenter le tour
        2. Classifier le mode (REFLEX / DELIBERATIVE)
        3. Router vers le traitement approprié
        4. Monitorer la sortie (GTO)
        5. Appliquer la modulation si délibératif
        6. Retourner la réponse finale
        """
        self.context.increment_turn()
        self.context.add_user_message(query)

        self.logger.info(
            f"\n{'='*60}\n"
            f"  Tour {self.context.turn_count} | "
            f"Phase: {self.context.phase} | "
            f"Mode: {self.context.mode or 'TBD'}\n"
            f"{'='*60}"
        )

        # 1. Classification du mode
        mode = self.mode_switch.classify(query, self.context)

        # 2. Traitement selon le mode
        if mode == "REFLEX":
            response_text = self._process_reflex(query)
        else:
            response_text = self._process_deliberative(query)

        # Sauvegarder la réponse dans le contexte
        self.context.add_assistant_message(response_text)

        return response_text

    def _process_reflex(self, query: str) -> str:
        """Traitement en mode REFLEX — rapide, direct, Haiku uniquement."""
        max_tokens = self.config["mode_switch"]["reflex_max_tokens"]
        return self.recruiter.process_reflex(query, self.context, max_tokens)

    def _process_deliberative(self, query: str, depth: int = 0) -> str:
        """Traitement en mode DELIBERATIVE — pipeline complet.

        Args:
            depth: profondeur de récursion (pour décomposition GTO)
        """
        # Garde-fou contre la récursion infinie
        if depth > 2:
            self.logger.warn("Profondeur max de décomposition atteinte")
            return self.recruiter.process_reflex(query, self.context, max_tokens=1024)

        # 1. Recrutement Henneman (escalade possible)
        response_text, evaluation = self.recruiter.process(query, self.context)

        # 2. Monitoring GTO
        gto_result = self.monitor.analyze(query, response_text, self.context)

        if gto_result["overloaded"] and gto_result["subtasks"]:
            # Surcharge détectée → décomposer et redistribuer
            self.logger.bio_event(
                "INHIBITION",
                action="decompose_and_redistribute",
                subtasks=len(gto_result["subtasks"])
            )
            response_text = self._handle_overload(
                query, gto_result["subtasks"], depth
            )

        # 3. Modulation (Reflex Reversal)
        response_text = self.modulator.modulate(
            response_text, query, self.context
        )

        return response_text

    def _handle_overload(self, original_query: str,
                         subtasks: list[str], depth: int) -> str:
        """Gère une surcharge : décompose et redistribue aux agents."""
        sub_responses = []

        for i, subtask in enumerate(subtasks, 1):
            self.logger.info(f"  Sous-tâche {i}/{len(subtasks)}: {subtask[:80]}")
            # Chaque sous-tâche repart du niveau 1 (Henneman)
            sub_text, _ = self.recruiter.process(subtask, self.context)

            # Vérifier la sous-réponse aussi (récursion limitée)
            sub_gto = self.monitor.analyze(subtask, sub_text, self.context)
            if sub_gto["overloaded"] and sub_gto["subtasks"] and depth < 2:
                sub_text = self._handle_overload(
                    subtask, sub_gto["subtasks"], depth + 1
                )

            sub_responses.append(f"## {subtask}\n{sub_text}")

        # Assembler les sous-réponses
        combined = (
            f"[Question décomposée en {len(subtasks)} parties]\n\n"
            + "\n\n---\n\n".join(sub_responses)
        )
        return combined

    def reset_session(self):
        """Réinitialise le contexte pour une nouvelle session."""
        self.context = SharedContext()
        self.logger.info("Session réinitialisée")

    def get_session_info(self) -> dict:
        """Retourne les informations de session courante."""
        return {
            "turn_count": self.context.turn_count,
            "mode": self.context.mode,
            "phase": self.context.phase,
            "refractory_counter": self.context.refractory_counter,
            "events_count": len(self.context.events),
        }
