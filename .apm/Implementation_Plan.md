# Vigilux – APM Implementation Plan
**Memory Strategy:** Dynamic-MD
**Last Modification:** Plan creation by the Setup Agent.
**Project Overview:** Vigilux is a competitive intelligence SaaS. Backend Phase 7 (Real Engines) is partially implemented (Apify/Celery files exist). **Current Priority:** Debugging existing backend logic and **Implementing the Frontend Integration** which is currently missing (UI is still static/mock).

## Phase 1: Foundation & Infrastructure (Completed/Maintenance)
*Reference Only - See existing codebase*

## Phase 2: Database Schema & Authentication (Completed/Maintenance)
*Reference Only - See existing codebase*

## Phase 3: Core Logic & Mocks (Completed/Maintenance)
*Reference Only - See existing codebase*

## Phase 4: Dashboard & UI Implementation (Completed/Maintenance)
*Reference Only - See existing codebase*

## Phase 5: Notifications & Integrations (Pending Future)
*Deferred until Real Engines are active*

## Phase 6: QA & Finalization (Continuous)
*Ongoing/Deferred*

## Phase 7: Real Engines & Frontend Integration (REVISED)

### Phase 7A: Backend Review & Fixes (Async/Scraping/AI)
*Note: Files for Apify/Celery exist. Manager must review and fix bugs.*

#### Task 7.1 – Backend Integrity Check - Agent_Backend_Async
**Objective:** Verify existing Celery/Redis/Apify implementation is bug-free.
**Output:** Bug fixes in `apify_client.py`, `celery_app.py`, and tasks.
**Guidance:**
1.  Vérifier que `celery_app.py` charge correctement la configuration et identifier les problèmes.
2.  Tester `ApifyService.scrape_google_maps` avec des identifiants valides et s'assurer de son fonctionnement.
3.  Vérifier que la logique de limitation de débit et de nouvelle tentative est active et fonctionne dans les tâches Celery.
4.  Appliquer les corrections nécessaires aux fichiers `apify_client.py`, `celery_app.py` et aux tâches.

#### Task 7.2 – Scheduler & Quota Debugging - Agent_Backend_Async
**Objective:** Ensure the tiered scheduling logic (Starter vs Ultimate) works.
**Output:** Fixes to `tasks/scheduler.py` (if exists) or create it.
**Guidance:**
1.  Vérifier la logique de `tasks/scheduler.py` (ou créer le fichier si absent) pour s'assurer que les utilisateurs "Growth" reçoivent uniquement des mises à jour hebdomadaires.
2.  Vérifier que les utilisateurs "Starter" sont bloqués des mises à jour automatiques.
3.  Appliquer les corrections nécessaires et tester la logique pour confirmer le respect des règles de quotas.

### Phase 7E: Real-time User Feedback (Backend Side)
*Note: Ensure WebSockets are ready.*

#### Task 7.3 – WebSocket Backend Verification - Agent_Backend_Async
**Objective:** Confirm `ws` endpoints and Redis PubSub are working.
**Output:** Working `/ws/notifications/{user_id}` endpoint.
**Guidance:**
**Depends on: Task 7.1 Output**
**Depends on: Task 7.2 Output**
1.  Vérifier la connectivité au endpoint WebSocket `/ws/notifications/{user_id}`.
2.  S'assurer que les tâches Celery émettent correctement les événements (`SCRAPING_STARTED`) via Redis PubSub.
3.  Confirmer que les événements émis par les tâches Celery sont bien reçus par le client WebSocket connecté.

### Phase 7F: Frontend Integration & UX Polish (CRITICAL NEW PHASE)

#### Task 7.4 – Onboarding Niche Selection Modal - Agent_Frontend_App
**Objective:** Force users to select a domain/niche upon first login (like a paywall/setup screen).
**Output:** `NicheSelectionModal` component and `UserContext` update.
**Guidance:**
1.  Implémenter la logique côté client pour vérifier si `user.niche` est défini. Si non, afficher un `NicheSelectionModal` bloquant.
2.  Développer le composant `NicheSelectionModal` permettant à l'utilisateur de choisir parmi une liste de niches prédéfinies (obtenues via une API ou un fichier de configuration).
3.  Mettre à jour le `UserContext` et envoyer la sélection de niche à l'API backend pour persistance.
4.  Assurer que l'accès au tableau de bord est bloqué tant que l'utilisateur n'a pas sélectionné et enregistré une niche.

#### Task 7.5 – Radar Chart & Spider Visualization - Agent_Frontend_App
**Objective:** Re-implement the Radar/Spider Chart using **Real Data** from the backend.
**Output:** `CompetitorRadarChart` component using Recharts.
**Guidance:**
**Depends on: Task 7.1 Output**
**Depends on: Task 7.2 Output**
1.  Récupérer les données réelles du graphique Radar depuis l'API `/api/v1/competitors/{id}/radar`.
2.  Implémenter le composant `CompetitorRadarChart` en utilisant Recharts, en mappant les attributs des concurrents (ex: Prix, Innovation, Portée) aux axes du graphique.
3.  Remplacer le placeholder statique existant dans la `RadarPage` par ce nouveau composant dynamique.

#### Task 7.6 – Async UX Integration (Progress Bars) - Agent_Frontend_Realtime
**Objective:** Connect the Dashboard to the WebSockets to show "Scanning...".
**Output:** Integrated `TaskProgress` component in `DashboardPage`.
**Guidance:**
**Depends on: Task 7.3 Output by Agent_Backend_Async**
1.  Établir une connexion WebSocket depuis le tableau de bord pour écouter les événements de progression des tâches.
2.  Lorsque l'événement `SCRAPING_STARTED` est reçu via WebSocket, remplacer l'affichage des cartes de statistiques par une barre de progression ou un état de chargement.
3.  Désactiver l'interaction utilisateur avec la carte du concurrent spécifique pendant la numérisation.
4.  Afficher une notification (toast) "Scan terminé. Nouvelles informations disponibles." à la réception d'un événement de fin de scan.
