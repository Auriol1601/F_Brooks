# F. Brooks

> Agent d'architecture logicielle pour le cadrage et la modélisation C4 - Niveau 1 (System Context)

![Status](https://img.shields.io/badge/status-beta-yellow)
![License](https://img.shields.io/badge/license-MIT-blue)

**F. Brooks** est un agent conçu pour assister les équipes de développement dans la phase de cadrage et de modélisation initiale (**SDLC - Phase 1 & 2**). Inspiré des principes du modèle C4, il transforme des descriptions fonctionnelles textuelles en un modèle de contexte rigoureux, structuré et visuel.

> 💡 Le nom rend hommage à Fred Brooks, auteur de *The Mythical Man-Month*, référence historique en gestion de projets logiciels.

---

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Démarrage rapide](#démarrage-rapide)
- [Exemple d'utilisation](#exemple-dutilisation)
- [Format de sortie](#format-de-sortie)
- [Hors périmètre](#hors-périmètre)
- [FAQ / Dépannage](#faq--dépannage)
- [Roadmap](#roadmap)
- [Contribuer](#contribuer)
- [Licence](#licence)

---

## Fonctionnalités

- **Cadrage itératif guidé** : accompagnement pas à pas pour identifier le cœur du système, sans questions techniques prématurées.
- **Modélisation C4 Niveau 1 (System Context)** : identification structurée de :
  - Le système étudié
  - Les utilisateurs humains (acteurs)
  - Les systèmes externes (tiers, API, passerelles)
  - Le sens fonctionnel exact des interactions
- **Génération automatique de code Structurizr DSL** : dès que le périmètre est validé (`VALID`), production du `workspace` prêt à l'emploi.
- **Visualisation locale instantanée** : rendu graphique en temps réel via Structurizr Lite.

### Pourquoi l'utiliser

| Problème courant | Réponse de F. Brooks |
|---|---|
| Erreurs de périmètre | Politique anti-hallucination stricte (pas d'invention d'acteurs ou de fonctionnalités) |
| Documentation hétérogène | Formalisme standardisé pour tous les diagrammes de contexte |
| Passage lent de l'idée au schéma | Décrire → valider → copier le DSL → visualiser |

---

## Prérequis

- [Structurizr Lite](https://structurizr.com/help/lite) (via Docker) pour la visualisation locale
- Docker installé et fonctionnel
- [pi agent](https://pi.dev) (Node.js) : environnement d'exécution de F. Brooks

---

## Installation

### 1. Installer pi agent (Windows)

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
```

Le flag `--ignore-scripts` désactive les scripts de cycle de vie des dépendances (non requis pour un usage normal de pi).

### 2. Lancer Structurizr Lite en local

```bash
docker run -it --rm -p 8080:8080 -v ~/structurizr:/usr/local/structurizr structurizr/lite
```

Le dossier `~/structurizr` doit contenir un fichier `workspace.dsl` (vide au départ, il sera rempli par F. Brooks).

---

## Démarrage rapide

1. **Initier le cadrage** : lancez une session avec F. Brooks en décrivant votre application et son objectif principal (ex. une solution de e-wallet).
2. **Affiner les frontières** : répondez à ses questions pour lister les utilisateurs réels et les systèmes externes indispensables.
3. **Récupérer le modèle** : dès que l'état passe à `VALID`, copiez le bloc de code Structurizr DSL généré.
4. **Visualiser** : collez le code dans `structurizr/workspace.dsl` et ouvrez [http://localhost:8080](http://localhost:8080).

---

## Exemple d'utilisation

```
Utilisateur : Je veux modéliser une solution de e-wallet mobile permettant
aux utilisateurs de transférer de l'argent et de payer des marchands.

F. Brooks : Très bien. Avant de construire le contexte, quelques précisions :
1. Qui sont les acteurs humains qui interagissent directement avec le système ?
2. Le e-wallet s'appuie-t-il sur des systèmes externes (banque, opérateur
   mobile money, passerelle de paiement) ?

Utilisateur : Les utilisateurs finaux et les marchands. Le système s'appuie
sur une passerelle bancaire (GIM-UEMOA) et un service SMS pour les OTP.

F. Brooks : Périmètre proposé :
- Acteurs : Utilisateur final, Marchand
- Systèmes externes : Passerelle GIM-UEMOA, Service SMS/OTP
- Système étudié : Application E-Wallet

État : VALID ✅

[workspace.dsl généré ci-dessous]
```

---

## Format de sortie

À la validation, F. Brooks génère un fichier Structurizr DSL de ce type :

```dsl
workspace {
    model {
        user = person "Utilisateur final"
        merchant = person "Marchand"

        ewallet = softwareSystem "Application E-Wallet"
        gimUemoa = softwareSystem "Passerelle GIM-UEMOA"
        smsGateway = softwareSystem "Service SMS/OTP"

        user -> ewallet "Transfère de l'argent, consulte son solde"
        merchant -> ewallet "Reçoit des paiements"
        ewallet -> gimUemoa "Autorise et route les transactions"
        ewallet -> smsGateway "Envoie les codes OTP"
    }

    views {
        systemContext ewallet {
            include *
            autoLayout
        }
    }
}
```

L'état `VALID` est signalé explicitement dans la réponse de l'agent avant que le code ne soit fourni.

---

## Hors périmètre

Pour rester concentré sur le cadrage global, F. Brooks **refuse catégoriquement** de concevoir ou d'introduire :

- Les détails d'architecture interne (microservices, bases de données, tables, classes, composants)
- Les spécifications techniques de bas niveau (API détaillées, endpoints, queues de messages, brokers)
- Les choix d'infrastructure cloud, de frameworks ou de déploiement
- Le code source applicatif

Si vous lui demandez ce type d'élément, il vous rappellera poliment qu'ils dépassent le périmètre du Niveau 1 - System Context.

> Pour les niveaux C4 supérieurs (Container, Component), aucun agent complémentaire n'est disponible à ce jour.

---

## FAQ / Dépannage

**`localhost:8080` ne répond pas**
Vérifiez que le conteneur Docker Structurizr Lite est bien lancé (`docker ps`) et que le volume monté contient bien `workspace.dsl`.

**F. Brooks semble halluciner un acteur non mentionné**
Signalez-le explicitement dans la conversation ; la politique anti-hallucination est stricte mais peut nécessiter une reformulation de votre description initiale.

**Puis-je revenir en arrière après un état `VALID` ?**
Oui, il suffit de rouvrir la discussion et de préciser les changements ; F. Brooks régénère le périmètre et le DSL correspondant.

---

## Roadmap

- [ ] Support du C4 Niveau 2 (Container)
- [ ] Export direct vers un dépôt Git
- [ ] Intégration CI pour la validation automatique des workspaces

---

## Contribuer

Les retours, suggestions et rapports de bug sont les bienvenus via les issues du dépôt.

---

## Licence

MIT

```
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