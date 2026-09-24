# F.Brooks
F. Brooks est une réflexion sur ce que devra être le SDLC à dans ça phase 1 et 2 à l'aire des agents IA  .Il est un agent spécialisé dans l'analyse et la représentation du contexte d'un système logiciel.  Sa mission initiale est de transformer une description fonctionnelle fournie par un utilisateur en un System Context Diagram selon le C4 Model .

# F. Brooks — V1.0.0

## Pipeline

```text
SPEC.md
   ↓
SYSTEM_PROMPT.md
   ↓
Gemini API
   ↓
TESTS.md
   ↓
results/
```

Pi n'est volontairement pas utilisé dans cette première boucle.

## 1. Configurer Gemini

PowerShell :

```powershell
$env:GEMINI_API_KEY="VOTRE_CLE"
```

Vous pouvez aussi choisir un modèle :

```powershell
$env:GEMINI_MODEL="gemini-2.5-flash"
```

## 2. Lancer un seul test

```powershell
python run_tests.py --test CTX-001
```

## 3. Lancer toute la suite

```powershell
python run_tests.py
```

Les réponses sont enregistrées dans `results/`.

## 4. Verdict

Le runner ne prétend pas juger automatiquement la qualité du raisonnement.

Pour V1, on conserve une revue humaine :

- PASS : le comportement respecte le test ;
- FAIL : le comportement viole la spécification ;
- REVIEW : comportement ambigu ou test à améliorer.

Cette étape est volontaire : elle permet de construire une vraie suite de régression avant d'automatiser le scoring.

## 5. Pourquoi cette architecture ?

`SPEC.md` décrit le comportement attendu.

`SYSTEM_PROMPT.md` traduit cette spécification pour Gemini.

`TESTS.md` définit les comportements observables.

`run_tests.py` permet d'exécuter exactement ces cas sans Pi.

Pi sera ajouté ensuite comme runtime/orchestrateur. Les tests resteront les mêmes.
