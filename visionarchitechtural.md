Oui. Je te propose de conserver cette vision comme un **document d'architecture de référence**, séparé de la SPEC fonctionnelle de F. Brooks. Il servira de boussole pour les prochaines étapes sans nous enfermer dans les détails d'implémentation.

# F. Brooks — Vision architecturale

## C4 Model, Structurizr et interface conversationnelle

**Version : 1.0.0**
**Statut : Vision / Architecture cible**
**Projet : F. Brooks**

---

## 1. Vision

F. Brooks est un agent spécialisé dans la **compréhension et la modélisation du contexte d'un système logiciel selon le C4 Model**.

L'objectif n'est pas de créer un nouvel outil de dessin de diagrammes.

F. Brooks doit plutôt :

1. comprendre le contexte fourni par l'ingénieur ;
2. identifier les éléments pertinents du modèle C4 ;
3. détecter les informations manquantes, ambiguës ou contradictoires ;
4. dialoguer avec l'utilisateur lorsque des précisions sont nécessaires ;
5. produire un modèle C4 structuré ;
6. transmettre ce modèle à Structurizr ;
7. laisser Structurizr assurer la représentation graphique du modèle.

La philosophie générale est donc :

> **F. Brooks comprend le système. Structurizr le représente.**

---

# 2. Principe architectural fondamental

F. Brooks ne doit pas devenir un moteur graphique.

Il ne doit pas avoir la responsabilité de :

* calculer les positions des éléments ;
* dessiner les flèches ;
* gérer les layouts ;
* gérer le zoom graphique ;
* gérer le rendu des diagrammes ;
* implémenter un moteur de diagrammes C4.

Ces responsabilités sont déléguées à Structurizr.

F. Brooks se concentre sur la partie intelligente :

```text
Comprendre
    ↓
Analyser
    ↓
Questionner
    ↓
Modéliser
    ↓
Produire le modèle C4
    ↓
Structurizr
    ↓
Représenter
```

---

# 3. C4 comme structure de navigation

Le C4 Model fournit naturellement une hiérarchie permettant de naviguer dans l'architecture.

```text
C4 Model
│
├── Level 1 — System Context
│      │
│      └── Personnes
│          Système étudié
│          Systèmes externes
│          Relations
│
├── Level 2 — Container
│      │
│      └── Applications
│          Services
│          Bases de données
│          Containers
│
├── Level 3 — Component
│      │
│      └── Composants internes
│
└── Level 4 — Code
       │
       └── Classes / implémentation
```

### V1 de F. Brooks

La première version de F. Brooks se concentre sur :

> **C4 Level 1 — System Context**

Elle doit donc principalement représenter :

* les personnes ;
* le système étudié ;
* les systèmes externes ;
* les relations entre ces éléments.

Les niveaux Container, Component et Code ne sont pas nécessaires pour la première version.

---

# 4. Le zoom C4 comme évolution naturelle

L'interface pourra évoluer progressivement vers une navigation par niveaux.

Exemple :

```text
System Context
      │
      │ exploration
      ▼
Container View
      │
      │ exploration
      ▼
Component View
      │
      │ exploration
      ▼
Code View
```

L'utilisateur pourra ainsi partir d'une vision globale puis approfondir progressivement.

Cela correspond directement à la philosophie du C4 Model :

> **commencer par une vision simple du système puis augmenter progressivement le niveau de détail.**

---

# 5. Architecture fonctionnelle cible

L'application F. Brooks est organisée autour de trois responsabilités principales :

```text
                    F. BROOKS
                        │
             ┌──────────┴──────────┐
             │                     │
          Chat UI             Diagram UI
             │                     │
             └──────────┬──────────┘
                        │
                        ▼
                F. BROOKS CORE
                        │
             ┌──────────┴──────────┐
             │                     │
          Analyse              Modèle C4
             │                     │
             └──────────┬──────────┘
                        │
                        ▼
                   Structurizr
                        │
                        ▼
                  Diagramme C4
```

---

# 6. Chat UI

Le premier espace de l'application est conversationnel.

Il permet à l'ingénieur de communiquer naturellement avec F. Brooks.

Exemple :

```text
Utilisateur :

Nous voulons créer une plateforme de gestion
des congés.

Employé → plateforme → demande de congé.
Le service RH reçoit les demandes.
```

F. Brooks peut alors :

* analyser le contexte ;
* identifier le système ;
* identifier les personnes ;
* identifier les relations ;
* détecter les informations manquantes ;
* poser une question si nécessaire.

Le chat reste le moyen principal d'interaction avec l'intelligence de F. Brooks.

---

# 7. Diagram UI

Le deuxième espace présente la représentation C4.

L'objectif est de créer une relation directe entre :

```text
Conversation
      ↕
Compréhension
      ↕
Modèle C4
      ↕
Diagramme
```

Le diagramme n'est donc pas un résultat statique.

Il représente **l'état courant de la compréhension de F. Brooks**.

---

# 8. Interface à deux panneaux

L'interface cible peut être organisée ainsi :

```text
┌─────────────────────────────────────────────────────────────┐
│                         F. BROOKS                           │
├──────────────────────────┬──────────────────────────────────┤
│                          │                                  │
│          CHAT            │          DIAGRAMME C4            │
│                          │                                  │
│ User                     │       ┌──────────────┐           │
│ ───────────────          │       │   Employé    │           │
│                          │       └──────┬───────┘           │
│ Brooks                   │              │                   │
│ J'ai identifié...        │              ▼                   │
│                          │       ┌──────────────┐           │
│ Brooks                   │       │   Système    │           │
│ Il manque...             │       │   étudié     │           │
│                          │       └──────┬───────┘           │
│ User                     │              │                   │
│ Le service RH valide...  │              ▼                   │
│                          │       ┌──────────────┐           │
│                          │       │  Service RH  │           │
│                          │       └──────────────┘           │
│                          │                                  │
├──────────────────────────┴──────────────────────────────────┤
│                     Message / Interaction                    │
└─────────────────────────────────────────────────────────────┘
```

Cette organisation permet à l'ingénieur de :

* converser avec F. Brooks ;
* observer immédiatement l'évolution du modèle ;
* détecter visuellement les éléments identifiés ;
* explorer progressivement le contexte.

---

# 9. Le diagramme comme « état de compréhension »

Une idée fondamentale de cette architecture est que le diagramme ne doit pas être considéré comme une simple illustration.

Il représente :

> **ce que F. Brooks comprend actuellement du système.**

Par conséquent, si une information est ambiguë, F. Brooks ne doit pas automatiquement inventer un élément.

Exemple :

```text
Utilisateur :

Les utilisateurs reçoivent des notifications
lorsque leur demande est traitée.
```

F. Brooks peut comprendre :

```text
Utilisateur
     │
     ▼
Système
     │
     ▼
[Notification]
```

mais ne doit pas décider automatiquement :

```text
Email
SMS
Firebase
Twilio
SendGrid
...
```

tant que le contexte ne l'établit pas.

Le modèle doit donc pouvoir rester incomplet ou signaler une information nécessitant clarification.

---

# 10. Responsabilités de F. Brooks

F. Brooks est responsable de la compréhension.

Il doit notamment :

### Analyse

* identifier le système étudié ;
* identifier les personnes ;
* identifier les systèmes externes ;
* identifier les relations ;
* déterminer le niveau C4 approprié.

### Qualité du contexte

* détecter les informations manquantes ;
* détecter les ambiguïtés ;
* détecter les contradictions ;
* éviter les inventions ;
* éviter la sur-modélisation.

### Dialogue

* poser les questions nécessaires ;
* expliquer pourquoi une information est nécessaire ;
* conserver les éléments déjà établis ;
* permettre la correction progressive du modèle.

### Modélisation

* construire le modèle C4 ;
* maintenir la cohérence du modèle ;
* produire le DSL Structurizr ;
* assurer la traçabilité entre les éléments du modèle et les informations fournies.

---

# 11. Responsabilités de Structurizr

Structurizr est responsable de la représentation.

Il peut notamment prendre en charge :

* la représentation du modèle C4 ;
* les vues System Context ;
* les vues Container ;
* les vues Component ;
* les layouts ;
* le positionnement des éléments ;
* les relations graphiques ;
* la navigation entre les vues ;
* le rendu du diagramme.

Le principe est :

```text
F. Brooks
    │
    │ Modèle C4 / DSL
    ▼
Structurizr
    │
    │ représentation
    ▼
Diagramme
```

---

# 12. Séparation des responsabilités

Cette architecture doit maintenir une séparation stricte.

| Responsabilité              | F. Brooks | Structurizr |
| --------------------------- | --------: | ----------: |
| Comprendre le contexte      |         ✓ |             |
| Poser des questions         |         ✓ |             |
| Détecter une ambiguïté      |         ✓ |             |
| Détecter une contradiction  |         ✓ |             |
| Identifier les acteurs      |         ✓ |             |
| Identifier le système       |         ✓ |             |
| Identifier les relations    |         ✓ |             |
| Construire le modèle C4     |         ✓ |             |
| Produire le DSL             |         ✓ |             |
| Représenter graphiquement   |           |           ✓ |
| Layout                      |           |           ✓ |
| Zoom / navigation graphique |           |           ✓ |
| Rendu des vues              |           |           ✓ |

Cette séparation constitue une règle architecturale importante du projet.

---

# 13. Modèle de données conceptuel

Le cœur de F. Brooks doit progressivement manipuler un modèle indépendant de l'interface graphique.

Conceptuellement :

```text
ContextModel
│
├── studiedSystem
│
├── people[]
│
├── externalSystems[]
│
├── relationships[]
│
├── contextState
│
├── traceability[]
│
└── uncertainties[]
```

Ce modèle peut ensuite être transformé en DSL Structurizr.

```text
ContextModel
      │
      ▼
Structurizr DSL
      │
      ▼
Structurizr
      │
      ▼
C4 View
```

Cette séparation permettra plus tard de changer l'interface sans modifier le moteur de compréhension.

---

# 14. Microfrontend

L'approche microfrontend est envisageable pour séparer les responsabilités d'interface.

Architecture conceptuelle :

```text
F. BROOKS FRONTEND
│
├── Chat Microfrontend
│   ├── conversation
│   ├── messages
│   └── interaction
│
├── Diagram Microfrontend
│   ├── System Context
│   ├── Container
│   ├── Component
│   └── navigation
│
└── Shared State
    ├── Context Model
    ├── current View
    └── analysis State
```

Cependant, le microfrontend ne doit pas devenir une contrainte inutile.

La priorité est :

> **simplicité d'installation et simplicité d'utilisation pour les ingénieurs.**

L'architecture technique pourra donc commencer avec une application frontend relativement simple, tout en conservant une séparation logique entre Chat UI et Diagram UI.

---

# 15. Installation cible

F. Brooks doit rester simple à installer.

L'objectif est de permettre à un ingénieur de passer rapidement de :

```text
Installation
      ↓
Lancement
      ↓
Chat avec F. Brooks
      ↓
Diagramme C4
```

sans devoir installer une chaîne complexe de développement.

Les détails d'infrastructure doivent rester invisibles autant que possible pour l'utilisateur final.

---

# 16. Gemini et moteur d'intelligence

Le modèle d'intelligence utilisé par F. Brooks est découplé du frontend.

Architecture :

```text
             Chat UI
                │
                ▼
          F. Brooks Core
                │
                ▼
          LLM Provider
                │
        ┌───────┴────────┐
        │                │
      Gemini          Local LLM
```

La V1 peut utiliser Gemini.

L'architecture ne doit toutefois pas rendre F. Brooks dépendant conceptuellement d'un seul fournisseur de modèle.

Le cœur doit rester :

```text
F. Brooks Core
      │
      └── Model Provider
```

---

# 17. Pipeline cible

Le pipeline global peut être résumé ainsi :

```text
┌───────────────┐
│    User       │
└───────┬───────┘
        │
        ▼
┌─────────────────────┐
│      Chat UI        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   F. Brooks Core    │
│                     │
│ Analyse             │
│ Validation          │
│ Questions           │
│ C4 Model            │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Context Model     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Structurizr DSL   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     Structurizr     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Diagram UI       │
└─────────────────────┘
```

---

# 18. Relation avec le Test Runner

Le `run_tests.py` reste un outil de développement et de régression.

Il ne fait pas partie de l'expérience utilisateur finale.

```text
                 F. BROOKS
                     │
          ┌──────────┴──────────┐
          │                     │
      Runtime UI            Test Runner
          │                     │
          │                 CTX-001
          │                 CTX-002
          │                 CTX-003
          │                   ...
          │                 CTX-010
          │                     │
          │                 Regression
          │
          ▼
      Utilisateur
```

Le Test Runner sert à vérifier que les évolutions du système ne dégradent pas les comportements attendus.

---

# 19. V1 — Périmètre recommandé

La première version de l'application doit rester volontairement limitée.

### V1 comprend

* conversation avec F. Brooks ;
* analyse C4 System Context ;
* `contextState` ;
* questions de clarification ;
* détection des ambiguïtés ;
* détection des contradictions ;
* génération du modèle ;
* génération du DSL Structurizr ;
* affichage du System Context ;
* mise à jour du diagramme après évolution du contexte ;
* sauvegarde du workspace Structurizr ;
* tests de régression.

### V1 ne comprend pas nécessairement

* éditeur graphique C4 personnalisé ;
* moteur de layout personnalisé ;
* architecture cloud ;
* génération de code ;
* génération automatique de microservices ;
* conception détaillée des bases de données ;
* génération d'API ;
* gestion complète de C4 Level 3/4.

---

# 20. Évolution future

Une fois le System Context stabilisé, F. Brooks pourra évoluer progressivement :

```text
V1
System Context
     │
     ▼
V2
Container
     │
     ▼
V3
Component
     │
     ▼
V4
Code / intégrations
```

L'important est de conserver la même philosophie :

```text
F. Brooks
    =
Compréhension + Modélisation

Structurizr
    =
Représentation + Navigation
```

---

# 21. Principe directeur du projet

Le principe directeur de cette architecture est :

> **Ne pas reconstruire ce que C4 et Structurizr savent déjà faire.**

F. Brooks doit apporter la valeur là où Structurizr n'est pas un agent conversationnel :

* compréhension du langage naturel ;
* raisonnement sur le contexte ;
* identification des éléments C4 ;
* gestion de l'incertitude ;
* dialogue avec l'ingénieur ;
* traçabilité ;
* contrôle de la qualité du modèle.

Structurizr prend ensuite en charge la représentation.

---

# 22. Architecture cible résumée

```text
                         ┌───────────────────────┐
                         │       INGÉNIEUR       │
                         └───────────┬───────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────┐
                    │          F. BROOKS          │
                    │                             │
                    │      Chat + Analyse         │
                    │                             │
                    │  Compréhension du contexte  │
                    │  Questions                  │
                    │  Validation                  │
                    │  C4 Model                    │
                    └──────────────┬──────────────┘
                                   │
                              Context Model
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │       STRUCTURIZR DSL       │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │         STRUCTURIZR         │
                    │                             │
                    │ System Context              │
                    │ Container                   │
                    │ Component                   │
                    │ Layout / Navigation         │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │         DIAGRAM UI          │
                    │                             │
                    │     Zoom C4 progressif      │
                    └─────────────────────────────┘
```

---

# 23. Conclusion

La direction retenue pour F. Brooks est donc une architecture **conversationnelle + représentation C4**, plutôt qu'un éditeur de diagrammes construit entièrement sur mesure.

Le cœur du produit est F. Brooks.

Structurizr constitue le moteur de représentation.

L'interface à deux panneaux permet de réunir les deux :

```text
             CONVERSATION
                  ↕
              F. BROOKS
                  ↕
             MODÈLE C4
                  ↕
             STRUCTURIZR
                  ↕
              DIAGRAMME
```

Cette architecture permet de garder F. Brooks :

* simple ;
* spécialisé ;
* évolutif ;
* compréhensible pour les ingénieurs ;
* indépendant de la complexité graphique ;
* compatible avec l'évolution progressive du C4 System Context vers Container puis Component.

**Décision architecturale de référence :**

> **F. Brooks est le cerveau conversationnel et de modélisation. Structurizr est le moteur de représentation C4.**
