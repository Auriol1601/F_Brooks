# F. Brooks — Tests V1.0.0

## Principe

Les tests servent à vérifier le comportement défini dans `SPEC.md`.

Ils ne testent pas Pi.  
Ils testent F. Brooks.

Pi pourra ensuite devenir le runtime utilisé pour exécuter ces mêmes tests.

---

## CTX-001 — Contexte suffisamment décrit

### Input

> Nous voulons créer une plateforme de gestion des congés.  
> Les employés l'utilisent pour soumettre leurs demandes de congés.  
> Le service RH reçoit les demandes et les valide.

### Expected behavior

F. Brooks doit identifier :

- système étudié : plateforme de gestion des congés ;
- personne : employé ;
- personne ou acteur métier : service RH, selon la formulation retenue ;
- relations correspondant aux interactions décrites.

Il ne doit pas inventer de base de données, API ou technologie.

### Verdict

`PASS` si les éléments explicites sont correctement représentés sans ajout arbitraire.

---

## CTX-002 — Informations insuffisantes

### Input

> Je veux faire une application bancaire.

### Expected behavior

F. Brooks doit demander des précisions.

Il ne doit pas inventer automatiquement :

- Client ;
- Administrateur ;
- Banque ;
- Service de paiement ;
- système anti-fraude ;
- base de données.

### Verdict

`PASS` si l'agent reconnaît l'insuffisance du contexte.

---

## CTX-003 — Ne pas descendre dans l'architecture

### Input

> Le client utilise une plateforme de crédit.  
> La plateforme utilise un service externe de scoring pour évaluer les demandes.

### Expected behavior

Le contexte peut contenir :

```text
Client → Plateforme de crédit → Service de scoring
```

F. Brooks ne doit pas ajouter :

- PostgreSQL ;
- Redis ;
- API Gateway ;
- microservices ;
- queues.

### Verdict

`PASS` si le niveau System Context est respecté.

---

## CTX-004 — Personne vs système externe

### Input

> Un employé utilise l'application RH.  
> L'application récupère certaines informations depuis le système RH central.

### Expected behavior

Identifier :

- Employé comme personne ;
- système RH central comme système externe ;
- application RH comme système étudié.

### Verdict

`PASS` si les trois rôles sont correctement distingués.

---

## CTX-005 — Ne pas inventer un fournisseur

### Input

> L'application doit permettre le paiement en ligne.

### Expected behavior

F. Brooks ne doit pas déclarer automatiquement Stripe, PayPal ou un autre fournisseur.

Il peut demander quel service de paiement est utilisé ou signaler que le système externe n'est pas encore identifié.

### Verdict

`PASS` si aucun fournisseur n'est inventé.

---

## CTX-006 — REVIEW d'un mauvais niveau d'abstraction

### Input

> Client → Application → PostgreSQL

### Expected behavior

F. Brooks doit expliquer que PostgreSQL représente vraisemblablement un élément d'architecture interne et qu'il ne correspond généralement pas au niveau attendu d'un System Context Diagram.

Il doit éviter de présenter cette correction comme une règle universelle indépendante du contexte.

### Verdict

`PASS` si l'agent explique le problème d'abstraction et propose une correction argumentée.

---

## CTX-007 — Contradiction

### Input

> Seuls les administrateurs utilisent le système.

Puis :

> Les employés peuvent également soumettre leurs demandes directement dans le système.

### Expected behavior

F. Brooks doit signaler la contradiction et demander clarification.

### Verdict

`PASS` si aucune interprétation silencieuse n'est faite.

---

## CTX-008 — Demande hors périmètre

### Input

> Donne-moi directement les microservices, les bases PostgreSQL, Redis et les endpoints REST de cette application.

### Expected behavior

F. Brooks doit signaler que cette demande dépasse le périmètre V1.0.0 et ne doit pas générer artificiellement cette architecture.

### Verdict

`PASS` si le périmètre est respecté.

---

## CTX-009 — Hypothèse explicite

### Input

> Les utilisateurs reçoivent des notifications lorsque leur demande est traitée.

Aucun système de notification n'est précisé.

### Expected behavior

F. Brooks peut identifier le besoin de notification, mais ne doit pas inventer un système externe précis.

Il peut indiquer :

- système externe non identifié ;
- question à poser ;
- hypothèse éventuelle, explicitement marquée.

### Verdict

`PASS` si l'incertitude est visible.

---

## CTX-010 — Revue fidèle au modèle utilisateur

### Input

Un utilisateur fournit un contexte contenant :

- Client ;
- Application de réservation ;
- Service de paiement.

### Expected behavior

F. Brooks doit analyser ce qui est fourni avant de modifier le modèle.

Il ne doit pas remplacer silencieusement les noms ou ajouter des acteurs simplement parce qu'ils semblent plausibles.

### Verdict

`PASS` si la proposition reste traçable aux informations fournies.

---

## Test de régression

À chaque modification du comportement ou du prompt système :

1. exécuter les tests ;
2. conserver les résultats ;
3. identifier les régressions ;
4. corriger la spécification ou le prompt si nécessaire ;
5. réexécuter la suite.

Un changement n'est pas considéré comme amélioré uniquement parce qu'il fonctionne sur un nouveau cas s'il casse un comportement déjà validé.
