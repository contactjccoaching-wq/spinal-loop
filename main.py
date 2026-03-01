"""
Spinal Loop — Point d'entrée CLI

Usage :
  python main.py "ta question"           → mode one-shot
  python main.py                          → mode interactif
  python main.py --config chemin.yaml     → config personnalisée
"""

import sys
import os
from pathlib import Path

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import SpinalLoopOrchestrator


# Couleurs ANSI
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BANNER = f"""
{CYAN}{BOLD}╔══════════════════════════════════════════╗
║     SPINAL LOOP ORCHESTRATOR v1.0        ║
║  Bio-inspired Multi-Agent System         ║
╚══════════════════════════════════════════╝{RESET}

{DIM}Commandes spéciales :{RESET}
  {YELLOW}quit / exit{RESET}    — quitter
  {YELLOW}status{RESET}         — état de la session
  {YELLOW}reset{RESET}          — nouvelle session
  {YELLOW}events{RESET}         — journal biologique
"""


def run_one_shot(query: str, config_path: str | None = None):
    """Exécute une requête unique et affiche la réponse."""
    orchestrator = SpinalLoopOrchestrator(config_path)
    response = orchestrator.process(query)
    print(f"\n{response}")
    orchestrator.logger.session_summary()


def run_interactive(config_path: str | None = None):
    """Mode interactif — boucle de conversation."""
    print(BANNER)

    # Vérifier la clé API
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(f"{YELLOW}ANTHROPIC_API_KEY non définie.{RESET}")
        print(f"Définissez-la : export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    orchestrator = SpinalLoopOrchestrator(config_path)

    while True:
        try:
            query = input(f"\n{GREEN}{BOLD}> {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{DIM}Au revoir.{RESET}")
            orchestrator.logger.session_summary()
            break

        if not query:
            continue

        # Commandes spéciales
        if query.lower() in ("quit", "exit", "q"):
            print(f"{DIM}Au revoir.{RESET}")
            orchestrator.logger.session_summary()
            break

        if query.lower() == "status":
            info = orchestrator.get_session_info()
            print(f"\n{CYAN}Session :{RESET}")
            for k, v in info.items():
                print(f"  {k}: {BOLD}{v}{RESET}")
            continue

        if query.lower() == "reset":
            orchestrator.reset_session()
            print(f"{YELLOW}Session réinitialisée.{RESET}")
            continue

        if query.lower() == "events":
            events = orchestrator.context.events
            if not events:
                print(f"{DIM}Aucun événement biologique enregistré.{RESET}")
            else:
                print(f"\n{CYAN}Événements biologiques :{RESET}")
                for e in events:
                    print(f"  {e.timestamp[11:19]} | "
                          f"{BOLD}{e.event_type}{RESET} | "
                          f"{e.details}")
            continue

        # Traitement de la requête
        try:
            response = orchestrator.process(query)
            print(f"\n{response}")
        except Exception as e:
            print(f"\n{YELLOW}Erreur : {e}{RESET}")


def main():
    config_path = None
    args = sys.argv[1:]

    # Parser --config
    if "--config" in args:
        idx = args.index("--config")
        if idx + 1 < len(args):
            config_path = args[idx + 1]
            args = args[:idx] + args[idx + 2:]
        else:
            print("Erreur : --config nécessite un chemin")
            sys.exit(1)

    if args:
        # Mode one-shot
        query = " ".join(args)
        run_one_shot(query, config_path)
    else:
        # Mode interactif
        run_interactive(config_path)


if __name__ == "__main__":
    main()
