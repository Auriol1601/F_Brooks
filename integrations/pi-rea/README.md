# Intégration REA ↔ pi

Connecte le serveur MCP [REA](https://github.com/morluto/rea) (`rea-agents`,
rétro-ingénierie de binaires, d'applications JS/Electron, Android et web) à
l'agent [pi](https://github.com/earendil-works/pi).

Ce dossier est indépendant de F. Brooks. Il est rangé dans ce dépôt pour que la
configuration soit versionnée.

## Prérequis

| Outil | Version validée | Rôle |
|---|---|---|
| pi (`@earendil-works/pi-coding-agent`) | 1.2.0 | Le support MCP natif (`mcp.json`) n'existe pas en 0.87.x |
| REA (`rea-agents`) | 6.5.0 | Serveur MCP, 207 outils |
| Node.js | ^22.19 ou ^24.11 | Requis par REA |

## Installation

```bash
npm install -g @earendil-works/pi-coding-agent@1.2.0 rea-agents
rea setup --client pi --dry-run --json   # relire le plan
rea setup --client pi --yes
```

Le setup :

- écrit l'entrée `mcpServers.rea` dans `~/.pi/agent/mcp.json` (portée
  utilisateur, donc REA est disponible dans tous les répertoires) ;
- installe le skill `reverse-engineer-anything` dans `~/.agents/skills/`, que
  pi découvre automatiquement.

[mcp.json](mcp.json) est la copie de référence de l'entrée produite sur ce
poste. Les chemins sont propres à la machine ; sur un autre poste, relancer
`rea setup` plutôt que copier le fichier.

## Vérification

```powershell
powershell -File integrations/pi-rea/check.ps1
```

Le script compare l'entrée active à la référence, puis lance `rea doctor
--client pi` et `pi mcp list`. Résultat attendu :
`rea: connected, 207 tools (codemode, global)`.

## Utilisation dans pi

Les outils sont exposés en `codemode` (valeur par défaut de pi), le mode adapté
à un serveur de cette taille : le modèle les découvre avec `searchTools()` au
lieu de recevoir 207 déclarations à chaque requête. Ils sont nommés
`mcp__rea__<outil>`.

- `/mcp` dans pi : état du serveur, reconnexion, activation par projet.
- `pi --no-mcp` : désactive MCP pour une exécution.
- Analyse native (Hopper, Ghidra, IDA, JADX) : configurer le fournisseur au
  préalable, voir `rea doctor`. L'analyse JavaScript/Electron statique n'en a
  pas besoin.

## Choix du contexte : F. Brooks ou REA

[.pi/mcp.json](../../.pi/mcp.json) désactive REA dans ce dépôt : pi lancé dans
`D:\F_Brooks` est F. Brooks seul (prompt `.pi/SYSTEM.md`). Ailleurs, pi
standard dispose de REA. Les observations REA parviennent à F. Brooks par
`automation/rea_probe.py`, pas par le MCP.

Raccourcis du profil PowerShell (politique d'exécution `RemoteSigned` requise) :

```powershell
function brooks { Push-Location D:\F_Brooks; try { pi --no-mcp @args } finally { Pop-Location } }
function rea-pi { pi @args }   # depuis le dossier de la cible
```

## Mise à jour et retrait

- Après une mise à jour de `rea-agents`, relancer `rea setup --client pi --yes`
  (l'enregistrement est figé sur la version qui a fait le setup), puis
  redémarrer pi.
- Désactiver dans un projet sans toucher à la config utilisateur : créer
  `.pi/mcp.json` avec `{ "mcpServers": { "rea": { "enabled": false } } }`
  (seulement dans un projet de confiance).
- Retrait complet : supprimer l'entrée `rea` de `~/.pi/agent/mcp.json`.
