#!/usr/bin/env python3
"""
Simulation locale du Spinal Loop Orchestrator.

Exécute 6 requêtes qui déclenchent les 4 mécanismes biologiques
sans aucun appel API réel. Toutes les réponses sont mockées.

Usage : python simulate.py
"""

import os
import sys
import time
import io
from pathlib import Path

# Forcer UTF-8 sur Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Fake API key pour instancier le client sans erreur
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-simulation-not-a-real-key"

sys.path.insert(0, str(Path(__file__).parent))


# ════════════════════════════════════════════════════════
#  MOCK CLIENT — Simule le SDK Anthropic
# ════════════════════════════════════════════════════════

class _MockUsage:
    def __init__(self, inp=50, out=30):
        self.input_tokens = inp
        self.output_tokens = out


class _MockBlock:
    def __init__(self, text):
        self.text = text


class _MockResp:
    def __init__(self, text, inp=50, out=30):
        self.content = [_MockBlock(text)]
        self.usage = _MockUsage(inp, out)


class _MockMessages:
    """Route chaque appel vers la bonne réponse mockée."""

    def create(self, *, model, max_tokens, messages, system=None):
        user_msg = messages[-1]["content"] if messages else ""
        sys_lower = (system or "").lower()

        # --- Classifier (mode_switch.py) ---
        if "classifier de requêtes" in sys_lower:
            return self._classify(user_msg)

        # --- Reflex agent (recruiter.py) ---
        if "réflexe ultra-rapide" in sys_lower:
            return self._reflex(user_msg)

        # --- Deliberative agent (recruiter.py) ---
        if "agent de niveau" in sys_lower:
            lvl = 3 if "niveau 3" in sys_lower else (2 if "niveau 2" in sys_lower else 1)
            return self._deliberative(user_msg, lvl)

        # --- Monitor GTO (monitor.py) ---
        if "moniteur de qualité" in user_msg or "GTO" in user_msg:
            return self._monitor(user_msg)

        # --- Modulator (modulator.py) ---
        if "modulateur en phase EXPLORATION" in user_msg:
            return self._modulate_exploration(user_msg)
        if "modulateur en phase CONSOLIDATION" in user_msg:
            return self._modulate_consolidation(user_msg)

        return _MockResp("[simulation] réponse par défaut")

    # ---- Classifier ----
    def _classify(self, query):
        q = query.lower()
        if any(kw in q for kw in ["capitale", "europe", "c'est en", "monnaie"]):
            return _MockResp(
                '{"mode": "REFLEX", "reason": "question factuelle simple"}',
                30, 15
            )
        return _MockResp(
            '{"mode": "DELIBERATIVE", "reason": "analyse complexe requise"}',
            30, 15
        )

    # ---- Reflex ----
    def _reflex(self, query):
        q = query.lower()
        if "capitale" in q:
            return _MockResp("La capitale de la France est Paris.", 20, 12)
        if "europe" in q or "c'est en" in q:
            return _MockResp(
                "Oui, la France est en Europe de l'Ouest.", 20, 15
            )
        if "monnaie" in q:
            return _MockResp("L'euro, depuis 2002.", 20, 10)
        return _MockResp("Réponse réflexe.", 20, 10)

    # ---- Deliberative agent ----
    def _deliberative(self, query, level):
        q = query.lower()

        # -- Kant/Nietzsche : escalade complète 1→2→3 --
        if "kant" in q or "nietzsche" in q:
            return self._kant_nietzsche(level)

        # -- Histoire informatique : GTO va détecter surcharge --
        if "histoire" in q and "informatique" in q:
            return self._informatique_overload()

        # -- Sous-tâches après décomposition GTO --
        if "pionniers" in q or "babbage" in q:
            return _MockResp(
                "Les pionniers : Babbage (machine analytique, 1837), "
                "Ada Lovelace (premier algorithme, 1843), "
                "Turing (machine universelle, 1936).\n\n"
                "<evaluation>\n"
                '{"confidence": 0.92, "complexity": 0.25, '
                '"escalate": false, "reason": "sous-tâche factuelle"}\n'
                "</evaluation>", 80, 55
            )
        if "matériel" in q or "hardware" in q or "transistor" in q:
            return _MockResp(
                "Évolution hardware : tubes à vide (1940s) → transistors "
                "(1947) → circuits intégrés (1958) → microprocesseurs "
                "(1971, Intel 4004) → quantique (2020s).\n\n"
                "<evaluation>\n"
                '{"confidence": 0.91, "complexity": 0.3, '
                '"escalate": false, "reason": "chronologie claire"}\n'
                "</evaluation>", 80, 50
            )
        if "logiciel" in q or "software" in q or "internet" in q:
            return _MockResp(
                "Ère logicielle : FORTRAN (1957) → UNIX (1969) → "
                "TCP/IP (1983) → WWW (1991) → Cloud (2006) → "
                "IA générative (2022).\n\n"
                "<evaluation>\n"
                '{"confidence": 0.90, "complexity": 0.3, '
                '"escalate": false, "reason": "chronologie logicielle"}\n'
                "</evaluation>", 80, 55
            )

        # -- Télétravail : modulation EXPLORATION --
        if "télétravail" in q or "avantages" in q:
            return _MockResp(
                "Les avantages du télétravail :\n"
                "1. Flexibilité horaire, meilleur équilibre vie pro/perso\n"
                "2. Réduction du trajet (-45 min/jour en moyenne)\n"
                "3. Productivité accrue (Stanford : +13%)\n"
                "4. Réduction des coûts immobiliers\n"
                "5. Vivier de talents élargi géographiquement\n\n"
                "<evaluation>\n"
                '{"confidence": 0.85, "complexity": 0.4, '
                '"escalate": false, "reason": "sujet bien documenté"}\n'
                "</evaluation>", 100, 110
            )

        # -- Synthèse --
        if "synthétise" in q or "synthèse" in q:
            return _MockResp(
                "Session couverte :\n"
                "- Géographie : France, Paris, Europe\n"
                "- Philosophie : Kant vs Nietzsche\n"
                "- Informatique : pionniers → hardware → IA\n"
                "- Travail : télétravail (+13% productivité)\n\n"
                "Fil rouge : tension structure vs liberté.\n\n"
                "<evaluation>\n"
                '{"confidence": 0.82, "complexity": 0.5, '
                '"escalate": false, "reason": "synthèse faisable"}\n'
                "</evaluation>", 140, 120
            )

        return _MockResp(
            "Réponse délibérative.\n\n"
            "<evaluation>\n"
            '{"confidence": 0.8, "complexity": 0.4, '
            '"escalate": false, "reason": "standard"}\n'
            "</evaluation>", 60, 50
        )

    def _kant_nietzsche(self, level):
        if level == 1:
            return _MockResp(
                "Kant et Nietzsche divergent sur la morale. "
                "Kant : impératif catégorique, morale universelle du devoir. "
                "Nietzsche : critique cette morale comme 'morale d'esclave'.\n\n"
                "<evaluation>\n"
                '{"confidence": 0.4, "complexity": 0.85, "escalate": true, '
                '"reason": "réponse superficielle, les critiques contemporaines '
                'dépassent ma capacité"}\n'
                "</evaluation>", 120, 90
            )
        if level == 2:
            return _MockResp(
                "L'éthique déontologique de Kant (Critique de la raison "
                "pratique, 1788) pose l'universalité via l'impératif "
                "catégorique. Nietzsche (Généalogie de la morale, 1887) "
                "renverse : la morale kantienne serait un instrument de "
                "domination des faibles, une 'morale du ressentiment'.\n\n"
                "Les critiques contemporaines nuancent cette opposition...\n\n"
                "<evaluation>\n"
                '{"confidence": 0.55, "complexity": 0.9, "escalate": true, '
                '"reason": "critiques contemporaines nécessitent analyse '
                'plus profonde"}\n'
                "</evaluation>", 200, 170
            )
        # level 3 (Opus)
        return _MockResp(
            "La tension Kant-Nietzsche structure la philosophie morale "
            "occidentale.\n\n"
            "**Kant** — L'impératif catégorique fonde la morale sur "
            "la raison pure pratique. La dignité humaine est "
            "inconditionnelle.\n\n"
            "**Nietzsche** — Toute morale a une histoire et une "
            "fonction de pouvoir. La 'morale des esclaves' inverse "
            "les valeurs nobles.\n\n"
            "**Critiques contemporaines :**\n"
            "- Rawls reprend Kant + 'voile d'ignorance'\n"
            "- Foucault radicalise Nietzsche via les dispositifs de pouvoir\n"
            "- MacIntyre (After Virtue) prône un retour aristotélicien\n"
            "- Butler articule Nietzsche et performativité\n\n"
            "La synthèse est peut-être impossible — mais c'est cette "
            "irréductibilité qui rend le dialogue fécond.\n\n"
            "<evaluation>\n"
            '{"confidence": 0.93, "complexity": 0.85, "escalate": false, '
            '"reason": "analyse complète avec sources et critiques"}\n'
            "</evaluation>", 300, 340
        )

    def _informatique_overload(self):
        """Réponse volontairement répétitive → GTO la détectera."""
        return _MockResp(
            "L'histoire de l'informatique est vaste. L'informatique "
            "commence avec les premiers calculs. Les calculs ont "
            "toujours été importants. L'histoire des calculs remonte "
            "loin. Les machines à calculer sont apparues.\n\n"
            "Charles Babbage a inventé la machine analytique. La machine "
            "analytique était une machine à calculer. Babbage a conçu "
            "cette machine à calculer.\n\n"
            "Alan Turing a créé la machine de Turing. La machine de "
            "Turing est un concept fondamental. Ce concept fondamental "
            "est important pour l'informatique.\n\n"
            "Les ordinateurs modernes sont apparus. Les ordinateurs ont "
            "évolué. L'évolution des ordinateurs a été rapide. Les "
            "ordinateurs sont devenus plus puissants. La puissance des "
            "ordinateurs augmente sans cesse.\n\n"
            "Internet est arrivé. Internet a changé le monde. Le monde "
            "a changé grâce à Internet. Le monde numérique est né.\n\n"
            "<evaluation>\n"
            '{"confidence": 0.75, "complexity": 0.5, "escalate": false, '
            '"reason": "sujet large mais traitable"}\n'
            "</evaluation>", 150, 230
        )

    # ---- Monitor GTO ----
    def _monitor(self, prompt):
        # Détecte la réponse "informatique overload" par son contenu
        if "L'histoire de l'informatique est vaste" in prompt:
            return _MockResp(
                '{"overloaded": true, '
                '"signals": {"repetitions": true, "excessive_length": true, '
                '"incoherence": false, "saturation": true}, '
                '"severity": 0.8, '
                '"subtasks": ['
                '"Les pionniers de l\'informatique (Babbage, Lovelace, Turing)", '
                '"L\'évolution du matériel hardware (tubes à vide au quantique)", '
                '"L\'ère logicielle et Internet (FORTRAN à l\'IA générative)"], '
                '"summary": "Réponse circulaire, répétitions excessives"}',
                100, 75
            )
        return _MockResp(
            '{"overloaded": false, '
            '"signals": {"repetitions": false, "excessive_length": false, '
            '"incoherence": false, "saturation": false}, '
            '"severity": 0.0, "subtasks": [], "summary": "OK"}',
            80, 35
        )

    # ---- Modulator ----
    def _modulate_exploration(self, prompt):
        p = prompt.lower()

        # Kant/Nietzsche → exploration philosophique
        if "kant" in p or "nietzsche" in p or "morale" in p:
            return _MockResp(
                "La tension Kant-Nietzsche structure la philosophie morale "
                "occidentale.\n\n"
                "**Kant** — L'imperatif categorique fonde la morale sur "
                "la raison pure pratique. Dignite inconditionnelle.\n\n"
                "**Nietzsche** — Toute morale a une histoire et une "
                "fonction de pouvoir. 'Morale des esclaves.'\n\n"
                "**Critiques :** Rawls, Foucault, MacIntyre, Butler\n\n"
                "**Perspectives divergentes (EXPLORATION) :**\n"
                "- Et si Kant et Nietzsche convergeaient sur l'autonomie "
                "individuelle, par des chemins opposes ?\n"
                "- Parallele neuro : le cerveau utilise-t-il des heuristiques "
                "rapides (Kant) ET un apprentissage contextuel (Nietzsche) ?\n"
                "- Les morales non-occidentales (confucianisme, ubuntu) "
                "dissolvent-elles cette opposition ?",
                200, 250
            )

        # Informatique (apres decomposition GTO)
        if "pionniers" in p or "hardware" in p or "logiciel" in p or "informatique" in p:
            return _MockResp(
                "**Histoire de l'informatique (3 axes) :**\n\n"
                "1. **Pionniers** — Babbage (1837), Lovelace (1843), "
                "Turing (1936)\n"
                "2. **Hardware** — Tubes a vide -> transistors (1947) -> "
                "circuits integres (1958) -> quantique (2020s)\n"
                "3. **Software** — FORTRAN (1957) -> UNIX (1969) -> "
                "WWW (1991) -> IA generative (2022)\n\n"
                "**Perspectives divergentes (EXPLORATION) :**\n"
                "- L'informatique est-elle une science ou un artisanat ?\n"
                "- L'evolution hardware mime la selection naturelle\n"
                "- Et si le prochain saut n'etait pas technique mais social ?",
                180, 200
            )

        # Default
        return _MockResp(
            "[Reponse preservee avec modulation exploratoire]\n\n"
            "**Perspectives divergentes :**\n"
            "- Connexion inattendue avec les systemes complexes\n"
            "- Et si l'hypothese de depart etait inversee ?\n"
            "- Angle non explore : dynamiques de pouvoir",
            100, 100
        )

    def _modulate_consolidation(self, prompt):
        return _MockResp(
            "**Synthèse consolidée :**\n\n"
            "1. **France** — Paris, Europe de l'Ouest (acquis)\n"
            "2. **Morale** — Kant (universalisme) vs Nietzsche "
            "(généalogie du pouvoir) : opposition irréductible "
            "mais féconde\n"
            "3. **Informatique** — 3 ères : pionniers théoriques → "
            "hardware → software/IA\n"
            "4. **Télétravail** — gains prouvés (+13% productivité) "
            "mais risque d'inégalité structurelle\n\n"
            "**Conclusion :** Chaque sujet révèle une tension "
            "structure/liberté. Prochaine étape : approfondir un axe.",
            150, 120
        )


class MockAnthropicClient:
    def __init__(self, **kwargs):
        self.messages = _MockMessages()


# ════════════════════════════════════════════════════════
#  SIMULATION
# ════════════════════════════════════════════════════════

# Couleurs
B = "\033[1m"
D = "\033[2m"
R = "\033[0m"
CY = "\033[96m"
GR = "\033[92m"
YE = "\033[93m"
MG = "\033[95m"
RD = "\033[91m"

SCENARIO = [
    {
        "query": "Quelle est la capitale de la France ?",
        "desc": "REFLEX — question factuelle simple",
        "mechanism": "Mode Switch → REFLEX, Haiku direct",
    },
    {
        "query": "C'est en Europe ?",
        "desc": "REFRACTORY — mode verrouillé (2 tours restants)",
        "mechanism": "Période réfractaire active → REFLEX maintenu",
    },
    {
        "query": "Et la monnaie utilisée ?",
        "desc": "REFRACTORY — dernier tour verrouillé",
        "mechanism": "Période réfractaire (dernier tour) → REFLEX",
    },
    {
        "query": "Compare les philosophies de Kant et Nietzsche sur la morale, "
                 "en intégrant les critiques contemporaines",
        "desc": "HENNEMAN — escalade Haiku → Sonnet → Opus",
        "mechanism": "Refractory expiré → SWITCH DELIBERATIVE + escalade 3 niveaux",
    },
    {
        "query": "Décris l'histoire complète de l'informatique depuis "
                 "les débuts jusqu'à aujourd'hui",
        "desc": "GTO — surcharge détectée → décomposition",
        "mechanism": "Haiku répond mal → GTO inhibe → 3 sous-tâches",
    },
    {
        "query": "Synthétise tout ce qu'on a discuté",
        "desc": "REVERSAL — keyword déclenche CONSOLIDATION",
        "mechanism": "Reflex Reversal → EXPLORATION bascule en CONSOLIDATION",
    },
]


def run_simulation():
    print(f"""
{CY}{B}╔══════════════════════════════════════════════════════════╗
║        SPINAL LOOP — SIMULATION LOCALE                   ║
║   4 mécanismes neuromusculaires × 6 requêtes             ║
╚══════════════════════════════════════════════════════════╝{R}

{D}Aucun appel API réel. Toutes les réponses sont mockées.{R}
{D}Les événements biologiques sont réels (même code de production).{R}
""")

    # Créer l'orchestrateur et injecter le mock
    from orchestrator import SpinalLoopOrchestrator
    orch = SpinalLoopOrchestrator()
    mock = MockAnthropicClient()
    orch.mode_switch.client = mock
    orch.recruiter.client = mock
    orch.monitor.client = mock
    orch.modulator.client = mock

    # Override : phase switch au tour 8 pour que REVERSAL soit déclenché
    # uniquement par le keyword "synthétise" (tour 6), pas par le compteur
    orch.modulator.phase_switch_turn = 8

    for i, scenario in enumerate(SCENARIO, 1):
        # En-tête du tour
        print(f"\n{YE}{'━'*60}{R}")
        print(f"{YE}{B}  TOUR {i}/6 — {scenario['desc']}{R}")
        print(f"{D}  Mécanisme attendu : {scenario['mechanism']}{R}")
        print(f"{YE}{'━'*60}{R}")
        time.sleep(0.3)

        # Requête
        print(f"\n{GR}{B}  > {scenario['query']}{R}\n")
        time.sleep(0.2)

        # Traitement
        response = orch.process(scenario["query"])

        # Réponse
        print(f"\n{CY}{'─'*40}{R}")
        print(f"{B}Réponse :{R}\n")
        print(response)
        print(f"\n{CY}{'─'*40}{R}")

        # État de la session
        info = orch.get_session_info()
        print(
            f"\n{D}  [état] tour={info['turn_count']} | "
            f"mode={info['mode']} | "
            f"phase={info['phase']} | "
            f"refractory={info['refractory_counter']} | "
            f"events={info['events_count']}{R}"
        )
        time.sleep(0.4)

    # Résumé final
    print(f"\n\n{MG}{B}{'═'*60}{R}")
    print(f"{MG}{B}  RÉSUMÉ DE LA SESSION{R}")
    print(f"{MG}{B}{'═'*60}{R}\n")

    orch.logger.session_summary()

    # Journal des événements biologiques
    print(f"\n{CY}{B}Événements biologiques enregistrés :{R}\n")
    for evt in orch.context.events:
        ts = evt.timestamp[11:19]
        color = {
            "SWITCH": CY, "ESCALADE": YE, "INHIBITION": RD,
            "REVERSAL": MG,
        }.get(evt.event_type, D)
        print(f"  {D}{ts}{R} | {color}{B}{evt.event_type:12}{R} | {D}{evt.details}{R}")

    print(f"\n{GR}{B}Simulation terminée.{R}\n")


if __name__ == "__main__":
    run_simulation()
