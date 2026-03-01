"""
Spinal Loop — Logger biologique

Log chaque événement du système avec son type biologique :
ESCALADE, INHIBITION, SWITCH, REVERSAL, RECRUIT, OVERLOAD, DECOMPOSE
"""

import logging
from datetime import datetime


# Couleurs ANSI pour le terminal
class _C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"


EVENT_STYLES = {
    "ESCALADE":  (_C.YELLOW,  "[ESCALADE]"),
    "INHIBITION": (_C.RED,    "[INHIBITION]"),
    "SWITCH":    (_C.CYAN,    "[SWITCH]"),
    "REVERSAL":  (_C.MAGENTA, "[REVERSAL]"),
    "RECRUIT":   (_C.GREEN,   "[RECRUIT]"),
    "OVERLOAD":  (_C.RED,     "[OVERLOAD]"),
    "DECOMPOSE": (_C.YELLOW,  "[DECOMPOSE]"),
    "CLASSIFY":  (_C.BLUE,    "[CLASSIFY]"),
    "MODULATE":  (_C.MAGENTA, "[MODULATE]"),
    "REFLEX":    (_C.GREEN,   "[REFLEX]"),
    "API_CALL":  (_C.DIM,     "[API]"),
}


class BioLogger:
    """Logger spécialisé pour les événements biologiques du système."""

    def __init__(self, log_file: str = "spinal_loop.log", level: str = "INFO"):
        self.logger = logging.getLogger("spinal_loop")
        self.logger.setLevel(getattr(logging, level, logging.INFO))
        self.logger.handlers.clear()

        # Fichier — log détaillé
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(logging.Formatter(
            "%(asctime)s | %(message)s", datefmt="%H:%M:%S"
        ))
        self.logger.addHandler(fh)

        # Console — log coloré
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(ch)

        self._total_input_tokens = 0
        self._total_output_tokens = 0
        self._call_count = 0

    def bio_event(self, event_type: str, model: str | None = None,
                  input_tokens: int = 0, output_tokens: int = 0, **kwargs):
        """Log un événement biologique."""
        color, label = EVENT_STYLES.get(event_type, (_C.DIM, f"[{event_type}]"))

        parts = [f"{color}{_C.BOLD}{label}{_C.RESET}"]
        if model:
            short_model = model.replace("claude-", "").split("-202")[0]
            parts.append(f"model={_C.CYAN}{short_model}{_C.RESET}")
        if input_tokens or output_tokens:
            parts.append(f"tokens={_C.DIM}{input_tokens}in/{output_tokens}out{_C.RESET}")
            self._total_input_tokens += input_tokens
            self._total_output_tokens += output_tokens
            self._call_count += 1
        for k, v in kwargs.items():
            parts.append(f"{k}={v}")

        self.logger.info(" | ".join(parts))

    def api_call(self, model: str, input_tokens: int, output_tokens: int,
                 event_type: str = "API_CALL"):
        """Raccourci pour logger un appel API."""
        self.bio_event(event_type, model=model,
                       input_tokens=input_tokens, output_tokens=output_tokens)

    def info(self, msg: str):
        self.logger.info(f"{_C.DIM}{msg}{_C.RESET}")

    def warn(self, msg: str):
        self.logger.warning(f"{_C.YELLOW}{msg}{_C.RESET}")

    def error(self, msg: str):
        self.logger.error(f"{_C.RED}{msg}{_C.RESET}")

    def session_summary(self):
        """Affiche un résumé de la session."""
        self.logger.info(
            f"\n{_C.BOLD}--- Session Summary ---{_C.RESET}\n"
            f"  API calls: {self._call_count}\n"
            f"  Total tokens: {self._total_input_tokens} in / "
            f"{self._total_output_tokens} out\n"
            f"  Total: {self._total_input_tokens + self._total_output_tokens}"
        )
