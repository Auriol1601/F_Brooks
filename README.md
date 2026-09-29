# F. Brooks

> Agent d'architecture logicielle pour le cadrage et la modélisation C4.

![Status](https://img.shields.io/badge/status-beta-yellow)
![License](https://img.shields.io/badge/license-MIT-blue)

**F. Brooks** est un agent conçu pour assister les équipes de développement dans les premières phases du cycle de développement logiciel (**SDLC**).

Il accompagne l'utilisateur dans le cadrage d'un système, identifie les éléments nécessaires à la construction de son contexte et peut produire une représentation **C4 - Niveau 1 : System Context** au format **Structurizr DSL**.

> 💡 Le nom rend hommage à Fred Brooks, auteur de *The Mythical Man-Month*, référence historique en ingénierie logicielle.

---

## Table des matières

* [Fonctionnalités](#fonctionnalités)
* [Prérequis](#prérequis)
* [Installation](#installation)
* [Démarrage rapide](#démarrage-rapide)
* [Exemple d'utilisation](#exemple-dutilisation)
* [États de contexte](#états-de-contexte)
* [Format de sortie](#format-de-sortie)
* [Visualisation](#visualisation)
* [Hors périmètre](#hors-périmètre)
* [FAQ / Dépannage](#faq--dépannage)
* [Roadmap](#roadmap)
* [Contribuer](#contribuer)
* [Licence](#licence)

---

## Fonctionnalités

### Cadrage guidé

F. Brooks accompagne l'utilisateur dans la clarification progressive du système à modéliser.

L'objectif est de distinguer :

* le système étudié ;
* les personnes ou acteurs qui interagissent avec lui ;
* les systèmes logiciels externes ;
* les relations fonctionnelles entre ces éléments ;
* les informations explicitement fournies et celles qui restent inconnues.

### Modélisation C4 - Niveau 1

F. Brooks se concentre actuellement sur le **System Context** du modèle C4.

Le contexte représente le système comme une boîte noire et permet notamment d'identifier :

* les personnes ;
* le système étudié ;
* les systèmes logiciels externes ;
* les interactions principales.

### Analyse de cohérence

F. Brooks ne cherche pas systématiquement à produire un diagramme.

Selon les informations fournies, il peut déterminer que le contexte est :

* `SUFFICIENT`
* `INSUFFICIENT`
* `AMBIGUOUS`
* `CONTRADICTORY`
* `OUT_OF_SCOPE`

Cette distinction permet notamment d'éviter de transformer automatiquement une description incomplète ou contradictoire en architecture fictive.

### Génération Structurizr

Lorsqu'un contexte est suffisamment défini pour être représenté au niveau System Context, F. Brooks peut produire un workspace **Structurizr DSL**.

Le workspace peut ensuite être utilisé directement avec Structurizr Lite pour obtenir la représentation graphique du contexte.

### Validation par scénarios

Le comportement de F. Brooks est vérifié à travers une suite de scénarios couvrant notamment :

* les contextes suffisamment décrits ;
* les informations insuffisantes ;
* les systèmes externes explicitement identifiés ;
* les ambiguïtés de niveau C4 ;
* les contradictions fonctionnelles ;
* les demandes hors périmètre ;
* l'analyse d'un contexte existant.

---

## Pourquoi l'utiliser

| Problème courant                                 | Réponse de F. Brooks                                        |
| ------------------------------------------------ | ----------------------------------------------------------- |
| Périmètre mal défini                             | Cadrage progressif du système                               |
| Acteurs inventés trop rapidement                 | Distinction entre éléments explicites et inconnus           |
| Confusion entre contexte et architecture interne | Respect du niveau C4 demandé                                |
| Informations contradictoires                     | Détection explicite des contradictions                      |
| Description trop vague                           | `contextState = INSUFFICIENT` et questions de clarification |
| Passage manuel vers un diagramme                 | Génération du workspace Structurizr                         |
| Validation difficile du comportement de l'agent  | Suite de scénarios automatisés                              |

---

## Prérequis

* [Structurizr Lite](https://structurizr.com/help/lite) pour la visualisation locale
* Docker installé et fonctionnel
* [pi](https://pi.dev/) comme environnement d'exécution et d'interaction avec l'agent

---

## Installation

### 1. Installer pi

Exemple d'installation sous Windows :

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
```

Le paramètre `--ignore-scripts` permet de désactiver les scripts de cycle de vie des dépendances lors de l'installation.

### 2. Lancer Structurizr Lite

```bash
docker run -it --rm -p 8080:8080 -v ~/structurizr:/usr/local/structurizr structurizr/lite
```

Le répertoire monté doit contenir le workspace Structurizr à visualiser.

---

## Démarrage rapide

### 1. Décrire le besoin

Commencez par décrire simplement le système que vous souhaitez modéliser.

Exemple :

```text
Nous voulons créer une plateforme de gestion des congés.
Les employés l'utilisent pour soumettre leurs demandes de congés.
Le service RH reçoit les demandes et les valide.
```

### 2. Laisser F. Brooks analyser le contexte

L'agent identifie notamment :

* le système étudié ;
* les acteurs ;
* les systèmes externes explicitement mentionnés ;
* les relations ;
* les informations manquantes ;
* les éventuelles contradictions.

### 3. Vérifier l'état du contexte

F. Brooks indique l'état du contexte.

Par exemple :

```text
contextState = SUFFICIENT
```

ou :

```text
contextState = INSUFFICIENT
```

Lorsque des informations sont nécessaires, l'agent pose des questions de clarification plutôt que d'inventer les éléments manquants.

### 4. Produire le modèle

Lorsque le contexte est suffisamment défini, un workspace Structurizr peut être généré et sauvegardé automatiquement.

### 5. Visualiser

Le workspace peut ensuite être ouvert avec Structurizr Lite :

```text
http://localhost:8080
```

---

## Exemple d'utilisation

### Contexte suffisamment défini

```text
Utilisateur :

Nous voulons créer une plateforme de gestion des congés.
Les employés l'utilisent pour soumettre leurs demandes de congés.
Le service RH reçoit les demandes et les valide.
```

F. Brooks identifie :

* **Système :** Plateforme de gestion des congés
* **Acteur :** Employés
* **Acteur :** Service RH
* **Relations :**

  * Employés → Plateforme de gestion des congés
  * Service RH → Plateforme de gestion des congés

L'état peut alors être :

```text
contextState = SUFFICIENT
```

Un workspace Structurizr peut être généré à partir de ces informations.

### Contexte insuffisant

```text
Utilisateur :

Je veux faire une application bancaire.
```

F. Brooks ne doit pas inventer automatiquement :

* les clients ;
* les conseillers ;
* un core banking ;
* une passerelle de paiement ;
* un fournisseur d'authentification.

Il identifie plutôt le manque d'informations :

```text
contextState = INSUFFICIENT
```

puis demande les précisions nécessaires.

### Contexte contradictoire

```text
Utilisateur :

Seuls les administrateurs utilisent le système.

Les employés peuvent également soumettre leurs demandes directement dans le système.
```

F. Brooks identifie la contradiction et ne choisit pas silencieusement une interprétation :

```text
contextState = CONTRADICTORY
```

### Demande hors périmètre

```text
Utilisateur :

Donne-moi directement les microservices,
les bases PostgreSQL, Redis et les endpoints REST.
```

Ces éléments relèvent de niveaux d'architecture plus détaillés que le System Context.

F. Brooks indique :

```text
contextState = OUT_OF_SCOPE
```

et ne génère pas artificiellement ces éléments.

---

## États de contexte

| État            | Signification                                                                                |
| --------------- | -------------------------------------------------------------------------------------------- |
| `SUFFICIENT`    | Les informations permettent de construire le contexte demandé.                               |
| `INSUFFICIENT`  | Des informations importantes manquent pour établir correctement le contexte.                 |
| `AMBIGUOUS`     | La demande peut être interprétée de plusieurs manières ou mélange des niveaux d'abstraction. |
| `CONTRADICTORY` | Deux ou plusieurs informations fournies sont incompatibles.                                  |
| `OUT_OF_SCOPE`  | La demande dépasse le périmètre actuellement traité par F. Brooks.                           |

---

## Format de sortie

Lorsqu'un contexte peut être représenté, F. Brooks peut produire un workspace Structurizr similaire à :

```dsl
workspace "Gestion des congés" {

    model {
        employe = person "Employé"
        serviceRH = person "Service RH"

        plateformeConges = softwareSystem "Plateforme de gestion des congés"

        employe -> plateformeConges "Soumet des demandes de congés"
        serviceRH -> plateformeConges "Reçoit et valide les demandes"
    }

    views {
        systemContext plateformeConges "SystemContext" {
            include *
            autoLayout
        }
    }
}
```

Le workspace est destiné à être visualisé avec Structurizr.

---

## Visualisation

La visualisation actuelle repose sur **Structurizr Lite**.

Une fois Structurizr Lite lancé, le workspace peut être consulté depuis :

```text
http://localhost:8080
```

Cette séparation permet à F. Brooks de se concentrer sur le **cadrage et la modélisation**, tandis que Structurizr assure la représentation graphique du modèle.

---

## Hors périmètre

Dans son état actuel, F. Brooks ne cherche pas à définir automatiquement :

* les microservices ;
* les bases de données ;
* les tables ;
* les classes ;
* les composants internes ;
* les endpoints REST ;
* les files de messages ;
* les brokers ;
* l'infrastructure cloud ;
* les choix de frameworks ;
* le code source applicatif.

Ces éléments appartiennent à des niveaux d'architecture plus détaillés ou à des décisions d'implémentation.

Le niveau actuellement ciblé est principalement :

```text
C4
└── Niveau 1 : System Context
```

---

## FAQ / Dépannage

### `localhost:8080` ne répond pas

Vérifiez que Structurizr Lite est bien lancé :

```bash
docker ps
```

Vérifiez également que le répertoire contenant le workspace est correctement monté dans le conteneur.

### Aucun workspace Structurizr n'est détecté

Cette situation peut être normale lorsque le contexte est :

* `INSUFFICIENT`
* `CONTRADICTORY`
* `OUT_OF_SCOPE`

Dans ces cas, F. Brooks peut volontairement ne produire aucun workspace.

### Le terminal affiche des caractères incorrects

La chaîne de traitement doit utiliser un encodage compatible avec **UTF-8**, notamment pour les caractères accentués et les symboles utilisés dans les échanges.

La gestion complète et homogène de l'encodage UTF-8 fait partie des travaux en cours.

### Un test échoue à cause du fournisseur de modèle

Les services de génération peuvent temporairement retourner des erreurs de disponibilité ou de capacité.

Un échec de communication avec le modèle ne doit pas être confondu avec un échec fonctionnel de F. Brooks.

---

## Roadmap

### En cours / prochaine étape

* [ ] Finaliser la gestion UTF-8 de la pipeline Structurizr
* [ ] Intégrer une interface de chat conversationnelle
* [ ] Améliorer la gestion et le versionnement des `workspace.dsl`
* [ ] Améliorer l'expérience de visualisation du modèle

### Évolution C4

* [ ] Intégrer le C4 Niveau 2 : **Container**
* [ ] Permettre une progression naturelle du contexte vers les conteneurs
* [ ] Étendre progressivement la visualisation aux niveaux C4 suivants

### À plus long terme

* [ ] Simplifier l'installation pour les ingénieurs
* [ ] Faciliter l'utilisation locale de F. Brooks
* [ ] Évaluer une interface conversationnelle locale/connectable
* [ ] Améliorer l'intégration entre conversation et représentation Structurizr

---

## Contribuer

Les retours, suggestions et rapports de bugs sont les bienvenus.

Les contributions doivent préserver les principes fondamentaux du projet :

* ne pas inventer silencieusement des éléments ;
* distinguer les informations explicites des informations inconnues ;
* respecter le niveau d'abstraction demandé ;
* signaler les contradictions ;
* maintenir une séparation claire entre cadrage et architecture détaillée.

---

## Licence

MIT

```text
Copyright (c) 2026 Devmindset-ci

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
