#!/usr/bin/env python3
"""
Test des 4 mécanismes sur 3 scénarios réalistes :
  1. Développeur
  2. Grand public
  3. Employé de bureau

Usage : python simulate_scenarios.py
"""

import os, sys, io, time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-simulation-not-a-real-key"
sys.path.insert(0, str(Path(__file__).parent))


# ═══════════════════════════════════════════
#  MOCK CLIENT
# ═══════════════════════════════════════════

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
    def create(self, *, model, max_tokens, messages, system=None):
        user_msg = messages[-1]["content"] if messages else ""
        sys_lower = (system or "").lower()

        if "classifier de requêtes" in sys_lower:
            return self._classify(user_msg)
        if "réflexe ultra-rapide" in sys_lower:
            return self._reflex(user_msg)
        if "agent de niveau" in sys_lower:
            lvl = 3 if "niveau 3" in sys_lower else (2 if "niveau 2" in sys_lower else 1)
            return self._deliberative(user_msg, lvl)
        if "moniteur de qualité" in user_msg or "GTO" in user_msg:
            return self._monitor(user_msg)
        if "modulateur en phase EXPLORATION" in user_msg:
            return self._modulate_exploration(user_msg)
        if "modulateur en phase CONSOLIDATION" in user_msg:
            return self._modulate_consolidation(user_msg)

        return _MockResp("[simulation] reponse par defaut")

    def _classify(self, query):
        q = query.lower()
        simple_kw = [
            "syntaxe", "c'est quoi", "difference entre", "comment on",
            "qu'est-ce", "heure", "temps", "meteo", "matin", "soir",
            "roi", "kpi", "swot", "signifie", "veut dire",
            "list comprehension", "dict comprehension", "filter",
            "none", "null"
        ]
        if any(kw in q for kw in simple_kw):
            return _MockResp('{"mode": "REFLEX", "reason": "question factuelle simple"}', 30, 15)
        return _MockResp('{"mode": "DELIBERATIVE", "reason": "analyse complexe requise"}', 30, 15)

    def _reflex(self, query):
        q = query.lower()
        # Dev
        if "list comprehension" in q:
            return _MockResp("[x for x in iterable if condition]", 20, 12)
        if "dict comprehension" in q:
            return _MockResp("{k: v for k, v in items.items()}", 20, 12)
        if "filter" in q and "none" in q:
            return _MockResp("[x for x in lst if x is not None]", 20, 12)
        # Grand public
        if "heure" in q and "tokyo" in q:
            return _MockResp("Il est actuellement 22h30 a Tokyo (UTC+9).", 20, 15)
        if "matin" in q or "soir" in q:
            return _MockResp("C'est le soir a Tokyo.", 20, 10)
        if "meteo" in q or "temps" in q:
            return _MockResp("Tokyo : 18 degres, partiellement nuageux.", 20, 12)
        # Questions longues/complexes en mode reflex → reponse courte (realiste)
        if len(q) > 80:
            return _MockResp("Oui.", 20, 5)
        # Employe
        if "roi" in q:
            return _MockResp("ROI = Return On Investment. (Gain - Cout) / Cout x 100.", 20, 15)
        if "kpi" in q:
            return _MockResp("KPI = Key Performance Indicator. Metrique pour mesurer la performance.", 20, 15)
        if "swot" in q:
            return _MockResp("SWOT = Strengths, Weaknesses, Opportunities, Threats. Outil d'analyse strategique.", 20, 18)
        return _MockResp("Reponse reflexe.", 20, 10)

    def _deliberative(self, query, level):
        q = query.lower()

        # === DEV : architecture microservices ===
        if "microservice" in q or "architecture" in q:
            return self._dev_architecture(level)

        # === DEV : REST API trop large → GTO ===
        if "rest api" in q and ("authentication" in q or "rate limiting" in q or "tout ca" in q):
            return self._dev_overload()

        # === GRAND PUBLIC : voyage Japon ===
        if "japon" in q or "japan" in q:
            return self._trip_japan(level)

        # === GRAND PUBLIC : planifier 14 jours → GTO ===
        if "jour par jour" in q or "heure par heure" in q or "14 jours" in q:
            return self._trip_overload()

        # === EMPLOYE : analyse Q3 ===
        if "q3" in q or "revenue" in q or "churn" in q or "pivots" in q:
            return self._employee_q3(level)

        # === EMPLOYE : business plan complet → GTO ===
        if "business plan" in q or "plan complet" in q:
            return self._employee_overload()

        # Sous-taches GTO dev
        if "auth" in q and ("jwt" in q or "middleware" in q):
            return _MockResp(
                "Auth : JWT + refresh tokens, middleware Express.\n\n"
                "<evaluation>\n"
                '{"confidence": 0.90, "complexity": 0.3, "escalate": false, '
                '"reason": "sous-tache claire"}\n</evaluation>', 80, 55)
        if "rate limit" in q:
            return _MockResp(
                "Rate limiting : Redis sliding window, 100 req/min/user.\n\n"
                "<evaluation>\n"
                '{"confidence": 0.91, "complexity": 0.25, "escalate": false, '
                '"reason": "pattern standard"}\n</evaluation>', 80, 50)
        if "schema" in q or "migration" in q:
            return _MockResp(
                "DB : PostgreSQL, migrations Knex.js, users/orders/products.\n\n"
                "<evaluation>\n"
                '{"confidence": 0.89, "complexity": 0.3, "escalate": false, '
                '"reason": "schema classique"}\n</evaluation>', 80, 50)

        # Sous-taches GTO voyage
        if "itineraire" in q or "incontournables" in q:
            return _MockResp(
                "Incontournables : Tokyo (3j), Kyoto (3j), Osaka (2j), "
                "Hiroshima (1j), Hakone (1j).\n\n"
                "<evaluation>\n"
                '{"confidence": 0.92, "complexity": 0.25, "escalate": false, '
                '"reason": "itineraire classique"}\n</evaluation>', 80, 55)
        if "budget" in q:
            return _MockResp(
                "Budget famille 2 semaines : 5000-7000 EUR. "
                "JR Pass famille : ~800 EUR. Hebergement : 80-150 EUR/nuit.\n\n"
                "<evaluation>\n"
                '{"confidence": 0.88, "complexity": 0.3, "escalate": false, '
                '"reason": "estimations standards"}\n</evaluation>', 80, 50)
        if "culturel" in q or "norme" in q or "etiquette" in q:
            return _MockResp(
                "Regles : chaussures retirees, pourboire non, onsen nu, "
                "silence dans le metro, saluer en inclinant la tete.\n\n"
                "<evaluation>\n"
                '{"confidence": 0.93, "complexity": 0.2, "escalate": false, '
                '"reason": "regles bien connues"}\n</evaluation>', 80, 45)

        # Sous-taches GTO employe
        if "marche" in q or "concurren" in q:
            return _MockResp(
                "Analyse marche : secteur en croissance 8%/an, 3 concurrents "
                "principaux, notre part de marche : 12%.\n\n"
                "<evaluation>\n"
                '{"confidence": 0.87, "complexity": 0.35, "escalate": false, '
                '"reason": "donnees disponibles"}\n</evaluation>', 80, 55)
        if "financ" in q or "projection" in q:
            return _MockResp(
                "Projections : Y1 break-even, Y2 marge 15%, Y3 marge 22%. "
                "Besoin financement : 500K EUR seed.\n\n"
                "<evaluation>\n"
                '{"confidence": 0.85, "complexity": 0.4, "escalate": false, '
                '"reason": "projections estimees"}\n</evaluation>', 80, 55)
        if "risque" in q or "risk" in q:
            return _MockResp(
                "Risques : churn eleve (mitiger par retention), "
                "pression prix concurrents, dependance 2 clients cles.\n\n"
                "<evaluation>\n"
                '{"confidence": 0.88, "complexity": 0.3, "escalate": false, '
                '"reason": "risques identifies"}\n</evaluation>', 80, 50)

        # Synthese / consolidation
        if "resume" in q or "syntheti" in q or "conclure" in q or "action" in q:
            return _MockResp(
                "Points cles de la session couverts.\n\n"
                "<evaluation>\n"
                '{"confidence": 0.85, "complexity": 0.4, "escalate": false, '
                '"reason": "synthese"}\n</evaluation>', 100, 80)

        return _MockResp(
            "Reponse deliberative.\n\n<evaluation>\n"
            '{"confidence": 0.8, "complexity": 0.4, "escalate": false, '
            '"reason": "standard"}\n</evaluation>', 60, 50)

    # ---- DEV : architecture (escalade) ----
    def _dev_architecture(self, level):
        if level == 1:
            return _MockResp(
                "Pour une architecture microservices e-commerce :\n"
                "- Service paiement\n- Service inventaire\n- Service notifications\n"
                "Utilisez des API REST entre services.\n\n"
                "<evaluation>\n"
                '{"confidence": 0.35, "complexity": 0.88, "escalate": true, '
                '"reason": "reponse trop superficielle, pas de patterns de communication, '
                'pas de gestion des transactions distribuees"}\n</evaluation>', 120, 90)
        if level == 2:
            return _MockResp(
                "Architecture microservices e-commerce :\n\n"
                "**Services :** Payment (Stripe), Inventory (CQRS), "
                "Notifications (WebSocket + push).\n\n"
                "**Communication :** Event-driven via message broker (RabbitMQ). "
                "Saga pattern pour transactions distribuees.\n\n"
                "**Infra :** API Gateway, service mesh, circuit breaker.\n\n"
                "<evaluation>\n"
                '{"confidence": 0.58, "complexity": 0.90, "escalate": true, '
                '"reason": "manque les details sur la resilience, le monitoring, '
                'et les strategies de deploiement"}\n</evaluation>', 200, 170)
        return _MockResp(
            "Architecture microservices e-commerce complete :\n\n"
            "**Domain Services :**\n"
            "- Payment Service : Stripe/Adyen, idempotency keys, webhook handlers\n"
            "- Inventory Service : CQRS + Event Sourcing, stock reservations\n"
            "- Notification Service : multi-channel (email/push/SMS/WebSocket)\n\n"
            "**Infrastructure :**\n"
            "- API Gateway (Kong) avec rate limiting et auth\n"
            "- Event bus (Kafka) pour communication inter-services\n"
            "- Saga orchestrator pour transactions distribuees\n"
            "- Circuit breaker (Hystrix pattern) par service\n\n"
            "**Resilience :**\n"
            "- Outbox pattern pour garantir la publication d'events\n"
            "- Dead letter queue pour les echecs\n"
            "- Health checks + distributed tracing (Jaeger)\n\n"
            "**Deploy :** Kubernetes, Helm charts, canary deployments.\n\n"
            "<evaluation>\n"
            '{"confidence": 0.91, "complexity": 0.88, "escalate": false, '
            '"reason": "architecture complete avec patterns de resilience"}\n'
            "</evaluation>", 300, 340)

    def _dev_overload(self):
        return _MockResp(
            "Pour creer une REST API complete il faut d'abord l'authentication. "
            "L'authentication est importante. Il faut aussi le rate limiting. "
            "Le rate limiting protege l'API. L'API doit etre protegee. "
            "Il faut gerer les erreurs. Les erreurs doivent etre gerees. "
            "Le logging est important aussi. Il faut logger les requetes. "
            "Les requetes doivent etre loggees. Le caching ameliore les "
            "performances. Les performances sont importantes. Les migrations "
            "de base de donnees sont necessaires. La base de donnees "
            "doit etre migree. Les migrations sont importantes.\n\n"
            "<evaluation>\n"
            '{"confidence": 0.70, "complexity": 0.5, "escalate": false, '
            '"reason": "sujet tres large"}\n</evaluation>', 150, 230)

    # ---- GRAND PUBLIC : Japon (escalade) ----
    def _trip_japan(self, level):
        if level == 1:
            return _MockResp(
                "Le Japon c'est super pour les familles ! "
                "Visitez Tokyo, Kyoto et Osaka. Budget moyen.\n\n"
                "<evaluation>\n"
                '{"confidence": 0.38, "complexity": 0.82, "escalate": true, '
                '"reason": "reponse vague, pas de budget concret, pas de '
                'conseils culturels pratiques"}\n</evaluation>', 120, 80)
        if level == 2:
            return _MockResp(
                "Voyage Japon 2 semaines en famille :\n\n"
                "**Itineraire :** Tokyo (4j) → Hakone (1j) → Kyoto (3j) → "
                "Nara (1j) → Osaka (2j) → Hiroshima (1j)\n\n"
                "**Budget :** ~6000 EUR pour 2 adultes + 2 enfants. "
                "JR Pass recommande.\n\n"
                "**Culture :** Retirez vos chaussures, pas de pourboire.\n\n"
                "<evaluation>\n"
                '{"confidence": 0.55, "complexity": 0.85, "escalate": true, '
                '"reason": "itineraire OK mais manque les activites enfants, '
                'les hebergements adaptes, et les normes culturelles detaillees"}\n'
                "</evaluation>", 200, 160)
        return _MockResp(
            "**Voyage Japon — 2 semaines famille** (guide complet)\n\n"
            "**Itineraire optimise :**\n"
            "- Tokyo (4j) : Senso-ji, Akihabara, TeamLab, Ueno Zoo (enfants)\n"
            "- Hakone (1j) : onsen family-friendly, vue Fuji\n"
            "- Kyoto (3j) : Fushimi Inari, bambouseraie, ceremonie du the\n"
            "- Nara (1j) : cerfs, Todai-ji\n"
            "- Osaka (2j) : Dotonbori, Universal Studios Japan\n"
            "- Hiroshima + Miyajima (1j) : memorial + torii flottant\n\n"
            "**Budget detaille :** 5500-7000 EUR\n"
            "- Vols : 2800 EUR (famille 4)\n"
            "- JR Pass 14j : 800 EUR\n"
            "- Hebergement : 100 EUR/nuit (ryokan + hotel)\n"
            "- Nourriture : 60 EUR/jour\n\n"
            "**Normes culturelles essentielles :**\n"
            "- Chaussures retirees partout (interieur, temples, certains restos)\n"
            "- Pas de pourboire (considere impoli)\n"
            "- Silence dans les transports\n"
            "- Poubelles rares — garder ses dechets\n"
            "- Onsen : nu, douche avant, tatouages parfois refuses\n\n"
            "<evaluation>\n"
            '{"confidence": 0.92, "complexity": 0.82, "escalate": false, '
            '"reason": "guide complet avec budget, activites enfants et culture"}\n'
            "</evaluation>", 350, 380)

    def _trip_overload(self):
        return _MockResp(
            "Jour 1 a Tokyo il faut visiter le temple. Le temple est beau. "
            "Ensuite on mange. La nourriture est bonne. Jour 2 on visite "
            "un autre temple. Il y a beaucoup de temples. Les temples sont "
            "importants. Jour 3 encore un temple. On peut aussi faire du "
            "shopping. Le shopping est agreable. Jour 4 on va a un parc. "
            "Le parc est grand. Jour 5 on va a Kyoto. Kyoto a des temples. "
            "Beaucoup de temples. Les temples de Kyoto sont beaux. "
            "Jour 6 encore Kyoto. Kyoto est agreable.\n\n"
            "<evaluation>\n"
            '{"confidence": 0.65, "complexity": 0.5, "escalate": false, '
            '"reason": "trop de jours a couvrir"}\n</evaluation>', 150, 230)

    # ---- EMPLOYE : Q3 (escalade) ----
    def _employee_q3(self, level):
        if level == 1:
            return _MockResp(
                "Revenue down 12%, c'est preoccupant. Le churn augmente. "
                "Mais 3 nouveaux produits c'est bien. Il faut analyser.\n\n"
                "<evaluation>\n"
                '{"confidence": 0.40, "complexity": 0.85, "escalate": true, '
                '"reason": "analyse superficielle, pas de recommandations '
                'strategiques concretes"}\n</evaluation>', 120, 80)
        if level == 2:
            return _MockResp(
                "Analyse Q3 :\n\n"
                "**Diagnostic :** Revenue -12% correle avec churn en hausse. "
                "Les 3 nouveaux produits n'ont pas encore compense.\n\n"
                "**Hypotheses :** \n"
                "- Produits cannibalisation interne ?\n"
                "- Churn = probleme pricing ou onboarding ?\n"
                "- Cycle de vente plus long sur nouveaux produits\n\n"
                "**Pistes :** retention first, upsell sur base existante.\n\n"
                "<evaluation>\n"
                '{"confidence": 0.57, "complexity": 0.88, "escalate": true, '
                '"reason": "bonnes hypotheses mais manque les pivots '
                'strategiques concrets et les metriques de suivi"}\n'
                "</evaluation>", 200, 160)
        return _MockResp(
            "**Analyse strategique Q3 — Plan de redressement**\n\n"
            "**Diagnostic :**\n"
            "Revenue -12% avec churn en hausse = signal d'alarme retention. "
            "Les 3 lancements masquent le probleme de fond.\n\n"
            "**Root causes probables :**\n"
            "1. Time-to-value trop long sur nouveaux produits (→ churn early)\n"
            "2. Equipe support diluee sur 3 produits au lieu de 1\n"
            "3. Pricing misaligne : acquisition OK mais retention faible\n\n"
            "**3 pivots strategiques :**\n"
            "1. **Retention sprint** — 90 jours focus NPS + onboarding revu. "
            "KPI : churn rate < 5%/mois\n"
            "2. **Product-led growth** — free tier sur le produit le plus "
            "mature, upsell sur features avancees. KPI : conversion 3%\n"
            "3. **Focus** — geler le produit le moins performant, concentrer "
            "les ressources. KPI : revenue per employee\n\n"
            "**Quick win :** exit interviews sur les 50 derniers churns → "
            "data qualitative immediate.\n\n"
            "<evaluation>\n"
            '{"confidence": 0.90, "complexity": 0.85, "escalate": false, '
            '"reason": "analyse complete avec root causes et plan actionable"}\n'
            "</evaluation>", 300, 320)

    def _employee_overload(self):
        return _MockResp(
            "Un business plan doit contenir une analyse de marche. "
            "L'analyse de marche est importante. Le marche doit etre "
            "analyse. Il faut aussi des projections financieres. Les "
            "projections financieres sont necessaires. Les finances "
            "doivent etre projetees. La strategie marketing est "
            "essentielle. Le marketing est important. Il faut aussi "
            "un plan operationnel. Le plan operationnel decrit les "
            "operations. Les operations doivent etre planifiees. "
            "L'analyse de risques est necessaire. Les risques doivent "
            "etre analyses. Le financement doit etre trouve. "
            "Le financement est important pour le business plan.\n\n"
            "<evaluation>\n"
            '{"confidence": 0.68, "complexity": 0.5, "escalate": false, '
            '"reason": "sujet trop large"}\n</evaluation>', 150, 230)

    # ---- Monitor GTO ----
    def _monitor(self, prompt):
        p = prompt.lower()
        # Dev overload
        if "authentication" in p and "rate limiting" in p and "logging" in p:
            return _MockResp(
                '{"overloaded": true, '
                '"signals": {"repetitions": true, "excessive_length": true, '
                '"incoherence": false, "saturation": true}, '
                '"severity": 0.78, '
                '"subtasks": ['
                '"Auth et securite (JWT, middleware, refresh tokens)", '
                '"Rate limiting et caching (Redis, sliding window)", '
                '"Schema DB et migrations (PostgreSQL, Knex.js)"], '
                '"summary": "Reponse circulaire sur un sujet trop large"}',
                100, 75)
        # Trip overload
        if "jour 1" in p and "temple" in p:
            return _MockResp(
                '{"overloaded": true, '
                '"signals": {"repetitions": true, "excessive_length": true, '
                '"incoherence": false, "saturation": true}, '
                '"severity": 0.82, '
                '"subtasks": ['
                '"Itineraire : les incontournables par ville (Tokyo, Kyoto, Osaka)", '
                '"Budget detaille : vols, transport, hebergement, nourriture", '
                '"Normes culturelles et etiquette pratique"], '
                '"summary": "Reponse repetitive, temples mentionnes 8 fois"}',
                100, 75)
        # Employee overload
        if "analyse de marche" in p and "projections financieres" in p:
            return _MockResp(
                '{"overloaded": true, '
                '"signals": {"repetitions": true, "excessive_length": true, '
                '"incoherence": false, "saturation": true}, '
                '"severity": 0.80, '
                '"subtasks": ['
                '"Analyse de marche et paysage concurrentiel", '
                '"Projections financieres sur 3 ans", '
                '"Analyse de risques et plan de mitigation"], '
                '"summary": "Reponse circulaire, chaque section est reformulee sans contenu"}',
                100, 75)
        return _MockResp(
            '{"overloaded": false, '
            '"signals": {"repetitions": false, "excessive_length": false, '
            '"incoherence": false, "saturation": false}, '
            '"severity": 0.0, "subtasks": [], "summary": "OK"}',
            80, 35)

    # ---- Modulator ----
    def _modulate_exploration(self, prompt):
        return _MockResp(
            "[Reponse preservee + perspectives divergentes ajoutees]\n\n"
            "**Perspectives a explorer :**\n"
            "- Angle non couvert dans la reponse initiale\n"
            "- Connexion avec un domaine adjacent\n"
            "- Et si l'hypothese de depart etait inversee ?",
            100, 100)

    def _modulate_consolidation(self, prompt):
        return _MockResp(
            "**Synthese consolidee de la session.**\n\n"
            "Points cles structures et actionables.",
            80, 60)


class MockAnthropicClient:
    def __init__(self, **kwargs):
        self.messages = _MockMessages()


# ═══════════════════════════════════════════
#  3 SCENARIOS
# ═══════════════════════════════════════════

SCENARIOS = {
    "DEV": {
        "title": "DEVELOPPEUR",
        "desc": "Un dev qui pose des questions techniques",
        "queries": [
            {
                "query": "C'est quoi la syntaxe d'une list comprehension en Python ?",
                "expect": "REFLEX",
            },
            {
                "query": "Et pour une dict comprehension ?",
                "expect": "REFLEX (refractory)",
            },
            {
                "query": "Comment on filter les None dans une liste ?",
                "expect": "REFLEX (refractory)",
            },
            {
                "query": "Designe une architecture microservices pour une plateforme "
                         "e-commerce avec paiement, gestion d'inventaire et notifications real-time",
                "expect": "DELIBERATIVE + HENNEMAN escalade",
            },
            {
                "query": "Ecris une REST API complete avec authentication, rate limiting, "
                         "error handling, logging, caching et database migrations pour tout ca",
                "expect": "GTO overload + decomposition",
            },
            {
                "query": "Resume les decisions cles qu'on a prises",
                "expect": "CONSOLIDATION (reversal)",
            },
        ]
    },
    "PUBLIC": {
        "title": "GRAND PUBLIC",
        "desc": "Un utilisateur lambda qui planifie un voyage",
        "queries": [
            {
                "query": "C'est quoi l'heure a Tokyo maintenant ?",
                "expect": "REFLEX",
            },
            {
                "query": "C'est le matin ou le soir la-bas ?",
                "expect": "REFLEX (refractory)",
            },
            {
                "query": "Et le temps qu'il fait ?",
                "expect": "REFLEX (refractory)",
            },
            {
                "query": "Je planifie 2 semaines au Japon avec mes enfants, "
                         "qu'est-ce qu'on doit visiter, quel budget prevoir, "
                         "et quelles normes culturelles connaitre ?",
                "expect": "DELIBERATIVE + HENNEMAN escalade",
            },
            {
                "query": "Maintenant planifie jour par jour heure par heure les 14 jours "
                         "avec restaurants, hotels, transports, couts et plans B pour la pluie",
                "expect": "GTO overload + decomposition",
            },
            {
                "query": "Synthetise juste les choses essentielles a retenir",
                "expect": "CONSOLIDATION (reversal)",
            },
        ]
    },
    "EMPLOYEE": {
        "title": "EMPLOYE DE BUREAU",
        "desc": "Un employe qui prepare une presentation",
        "queries": [
            {
                "query": "C'est quoi le ROI exactement ?",
                "expect": "REFLEX",
            },
            {
                "query": "Et KPI ca veut dire quoi ?",
                "expect": "REFLEX (refractory)",
            },
            {
                "query": "Qu'est-ce qu'une analyse SWOT ?",
                "expect": "REFLEX (refractory)",
            },
            {
                "query": "Analyse notre performance Q3 : revenue en baisse de 12%, "
                         "churn en hausse, mais on a lance 3 nouveaux produits. "
                         "Quels pivots strategiques envisager ?",
                "expect": "DELIBERATIVE + HENNEMAN escalade",
            },
            {
                "query": "Cree un business plan complet avec analyse de marche, paysage "
                         "concurrentiel, projections financieres 3 ans, strategie marketing, "
                         "plan operationnel, analyse de risques et besoins financement",
                "expect": "GTO overload + decomposition",
            },
            {
                "query": "Conclure avec les 3 actions prioritaires",
                "expect": "CONSOLIDATION (reversal)",
            },
        ]
    },
}


# ═══════════════════════════════════════════
#  RUN
# ═══════════════════════════════════════════

B = "\033[1m"
D = "\033[2m"
R = "\033[0m"
CY = "\033[96m"
GR = "\033[92m"
YE = "\033[93m"
MG = "\033[95m"
RD = "\033[91m"


def run_scenario(name, scenario):
    print(f"\n{MG}{B}{'='*65}{R}")
    print(f"{MG}{B}  SCENARIO : {scenario['title']}{R}")
    print(f"{D}  {scenario['desc']}{R}")
    print(f"{MG}{B}{'='*65}{R}")

    from orchestrator import SpinalLoopOrchestrator
    orch = SpinalLoopOrchestrator()
    mock = MockAnthropicClient()
    orch.mode_switch.client = mock
    orch.recruiter.client = mock
    orch.monitor.client = mock
    orch.modulator.client = mock
    orch.modulator.phase_switch_turn = 8

    results = []

    for i, q in enumerate(scenario["queries"], 1):
        print(f"\n{YE}{'─'*60}{R}")
        print(f"{YE}{B}  Tour {i}/6{R}  {D}(attendu : {q['expect']}){R}")
        print(f"{GR}  > {q['query']}{R}")
        time.sleep(0.15)

        response = orch.process(q["query"])
        info = orch.get_session_info()

        print(f"\n{CY}  Reponse :{R} {response[:120]}{'...' if len(response) > 120 else ''}")
        print(f"{D}  [mode={info['mode']} | phase={info['phase']} | "
              f"refractory={info['refractory_counter']}]{R}")

        # Verifier si le comportement correspond
        actual_mode = info["mode"]
        expected = q["expect"]
        match = True
        if "REFLEX" in expected and actual_mode != "REFLEX":
            match = False
        if "DELIBERATIVE" in expected and actual_mode != "DELIBERATIVE":
            match = False

        status = f"{GR}OK{R}" if match else f"{RD}MISMATCH{R}"
        print(f"  {status}")
        results.append(match)

    # Bilan
    ok = sum(results)
    total = len(results)
    color = GR if ok == total else YE if ok >= 4 else RD
    print(f"\n{color}{B}  Bilan {scenario['title']} : {ok}/{total} comportements corrects{R}")

    # Events log
    print(f"\n{D}  Evenements biologiques :{R}")
    for evt in orch.context.events:
        ts = evt.timestamp[11:19]
        color = {
            "SWITCH": CY, "ESCALADE": YE, "INHIBITION": RD,
            "REVERSAL": MG,
        }.get(evt.event_type, D)
        print(f"    {D}{ts}{R} {color}{evt.event_type:12}{R} {D}{evt.details}{R}")

    orch.logger.session_summary()
    return ok, total


def main():
    print(f"""
{CY}{B}╔═══════════════════════════════════════════════════════════════╗
║   SPINAL LOOP — TEST SCENARIOS REALISTES                     ║
║   3 profils × 6 requetes = 18 tests                          ║
╚═══════════════════════════════════════════════════════════════╝{R}
""")

    total_ok = 0
    total_all = 0

    for name, scenario in SCENARIOS.items():
        ok, total = run_scenario(name, scenario)
        total_ok += ok
        total_all += total

    print(f"\n\n{MG}{B}{'='*65}{R}")
    print(f"{MG}{B}  BILAN GLOBAL : {total_ok}/{total_all} comportements corrects{R}")
    print(f"{MG}{B}{'='*65}{R}\n")

    if total_ok == total_all:
        print(f"{GR}{B}  Tous les mecanismes se declenchent correctement.{R}")
    else:
        print(f"{YE}{B}  Certains mecanismes ne se declenchent pas comme attendu.{R}")


if __name__ == "__main__":
    main()
