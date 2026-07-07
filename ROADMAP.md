# ROADMAP - Vigilux

Ce document détaille toutes les fonctionnalités et tâches techniques à développer pour le projet Vigilux. Chaque fonctionnalité est décomposée en tâches précises avec des critères d'acceptation clairs.

**Approche de développement :** Développer une fonctionnalité à la fois, tester qu'elle fonctionne complètement avant de passer à la suivante.

---

## Légende des Statuts

- ✅ **Complété** : Fonctionnalité testée et fonctionnelle
- 🔄 **En cours** : Travail en progression
- ⚠️ **Partiellement fait** : Code existe mais incomplet ou non testé
- ❌ **À faire** : Pas encore commencé

---

## PHASE 0 : Configuration et Infrastructure

### F0.1 - Configuration de l'Environnement de Développement

**Objectif :** Mettre en place un environnement de travail propre et reproductible avec toutes les bonnes pratiques.

#### Tâche 0.1.1 : Configuration Docker ✅
- **Description :** Vérifier et documenter la configuration Docker Compose
- **Fichiers concernés :** `docker-compose.yml`, `.dockerignore`
- **Critères d'acceptation :**
  - [ ] `docker-compose up --build` démarre tous les services sans erreur
  - [ ] Les 7 services (db, redis, api, worker, beat, flower, web) sont opérationnels
  - [ ] Les volumes persistent les données (PostgreSQL, Redis)
  - [ ] Les services peuvent communiquer entre eux
  - [ ] Hot-reload fonctionne pour le développement (backend et frontend)
- **Commandes de test :**
  ```bash
  docker-compose up -d
  docker-compose ps  # Vérifier que tous les services sont "Up"
  docker-compose logs api  # Vérifier qu'il n'y a pas d'erreurs
  ```

#### Tâche 0.1.2 : Configuration des Variables d'Environnement ⚠️
- **Description :** Créer un système de gestion des secrets sécurisé
- **Fichiers concernés :** `.env`, `.env.example`, `backend/app/core/config.py`
- **Critères d'acceptation :**
  - [ ] `.env.example` contient toutes les variables nécessaires avec des descriptions
  - [ ] Les secrets sensibles (API keys, SECRET_KEY) ne sont jamais commitées sur Git
  - [ ] `.gitignore` contient bien `.env`
  - [ ] Documentation claire sur où obtenir chaque API key (Apify, Gemini)
  - [ ] SECRET_KEY est généré de manière sécurisée (pas hardcodé)
- **Variables requises :**
  ```bash
  # Base de données
  DATABASE_URL=postgresql://vigilux:password@db:5432/vigilux

  # Redis
  REDIS_URL=redis://redis:6379/0

  # Sécurité
  SECRET_KEY=<générer avec: openssl rand -hex 32>
  ACCESS_TOKEN_EXPIRE_MINUTES=30

  # Services externes
  APIFY_API_TOKEN=<obtenir sur apify.com>
  GEMINI_API_KEY=<obtenir sur ai.google.dev>

  # Notifications (optionnel pour l'instant)
  SENDGRID_API_KEY=
  TWILIO_ACCOUNT_SID=
  TWILIO_AUTH_TOKEN=
  TWILIO_PHONE_NUMBER=
  ```

#### Tâche 0.1.3 : Standards de Code et Linting ⚠️
- **Description :** Configurer les outils de qualité de code
- **Fichiers concernés :** `.pre-commit-config.yaml`, `pyproject.toml`, `.eslintrc.json`
- **Critères d'acceptation :**
  - [ ] Backend : Black, Flake8, isort, mypy configurés
  - [ ] Frontend : ESLint, Prettier configurés
  - [ ] Pre-commit hooks installés et fonctionnels
  - [ ] Document CONTRIBUTING.md avec les règles de code
- **Commandes de test :**
  ```bash
  # Backend
  cd backend
  black . --check
  flake8 .
  mypy app/

  # Frontend
  cd frontend
  npm run lint
  npm run format:check
  ```

#### Tâche 0.1.4 : Configuration Git et Bonnes Pratiques ❌
- **Description :** Définir les règles de commit et branches
- **Fichiers concernés :** `.github/PULL_REQUEST_TEMPLATE.md`, `CONTRIBUTING.md`
- **Critères d'acceptation :**
  - [ ] Convention de commit définie (ex: Conventional Commits)
  - [ ] Template de Pull Request créé
  - [ ] Branches protégées configurées (main ne peut pas recevoir de push direct)
  - [ ] Documentation sur le workflow Git (feature branches, rebase vs merge)
- **Format de commit recommandé :**
  ```
  type(scope): description courte

  Corps du message avec plus de détails

  Fixes #123
  ```
  Types : `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

---

### F0.2 - Configuration GitHub et CI/CD

#### Tâche 0.2.1 : GitHub Actions - Tests Automatisés ⚠️
- **Description :** Pipeline CI pour tester le code à chaque push
- **Fichiers concernés :** `.github/workflows/test.yml`
- **Critères d'acceptation :**
  - [ ] Tests backend s'exécutent automatiquement sur chaque PR
  - [ ] Tests frontend s'exécutent automatiquement sur chaque PR
  - [ ] Linting vérifié automatiquement
  - [ ] Badge de statut des tests dans le README
  - [ ] Les PRs ne peuvent être mergées si les tests échouent
- **Exemple de workflow :**
  ```yaml
  name: Tests
  on: [push, pull_request]
  jobs:
    backend-tests:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - uses: actions/setup-python@v4
        - run: cd backend && pip install -r requirements.txt
        - run: cd backend && pytest

    frontend-tests:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - uses: actions/setup-node@v3
        - run: cd frontend && npm install
        - run: cd frontend && npm test
  ```

#### Tâche 0.2.2 : GitHub Actions - Build et Déploiement ❌
- **Description :** Pipeline CD pour déployer en staging/production
- **Fichiers concernés :** `.github/workflows/deploy.yml`
- **Critères d'acceptation :**
  - [ ] Build Docker réussi sur chaque push vers main
  - [ ] Déploiement automatique en staging après merge
  - [ ] Déploiement manuel en production (avec approbation)
  - [ ] Rollback automatique en cas d'échec
- **À définir plus tard :** Infrastructure de déploiement (AWS, DigitalOcean, Railway, etc.)

#### Tâche 0.2.3 : Configuration des Secrets GitHub ❌
- **Description :** Stocker les secrets de manière sécurisée dans GitHub
- **Critères d'acceptation :**
  - [ ] Secrets ajoutés dans GitHub Settings > Secrets and variables
  - [ ] Documentation sur quels secrets sont nécessaires
  - [ ] Les workflows utilisent `${{ secrets.SECRET_NAME }}` au lieu de valeurs en dur

---

### F0.3 - Configuration de la Base de Données

#### Tâche 0.3.1 : Révision du Schéma de Base de Données ⚠️
- **Description :** Vérifier et documenter le schéma actuel
- **Fichiers concernés :** `backend/app/models/*.py`, `backend/alembic/versions/*.py`
- **Critères d'acceptation :**
  - [ ] Diagramme ERD (Entity Relationship Diagram) créé
  - [ ] Tous les modèles documentés avec docstrings
  - [ ] Relations entre tables clairement définies
  - [ ] Index de performance ajoutés sur les colonnes fréquemment requêtées
- **Modèles actuels :**
  - User (id, email, hashed_password, plan, trial_until, niche)
  - Project (id, name, user_id, created_at)
  - Competitor (id, name, url, threat_score, tracking_enabled, last_scanned_at, project_id)
  - Event (id, type, description, score, metadata, competitor_id, detected_at)
  - NotificationSetting (id, user_id, email_enabled, webhook_enabled, slack_enabled, sms_enabled, webhook_url, slack_webhook_url)

#### Tâche 0.3.2 : Migrations Alembic - Vérification ✅
- **Description :** S'assurer que les migrations fonctionnent correctement
- **Fichiers concernés :** `backend/alembic/`
- **Critères d'acceptation :**
  - [ ] `alembic upgrade head` crée toutes les tables sans erreur
  - [ ] `alembic downgrade -1` et `alembic upgrade +1` fonctionnent
  - [ ] Toutes les migrations sont testées
  - [ ] Documentation sur comment créer une nouvelle migration
- **Commandes de test :**
  ```bash
  docker-compose exec api alembic current  # Voir la version actuelle
  docker-compose exec api alembic history  # Voir l'historique
  docker-compose exec api alembic upgrade head
  ```

#### Tâche 0.3.3 : Seed Data - Données de Test ✅
- **Description :** Script pour créer des données de test réalistes
- **Fichiers concernés :** `backend/app/db/seed.py`
- **Critères d'acceptation :**
  - [ ] Script crée 3 utilisateurs (un par plan)
  - [ ] Chaque utilisateur a 1 projet avec plusieurs concurrents
  - [ ] Événements réalistes générés pour tester les graphiques
  - [ ] Script peut être lancé plusieurs fois sans erreur (idempotent)
- **Commande :**
  ```bash
  docker-compose exec api python -m app.db.seed
  ```

---

## PHASE 1 : Fonctionnalités Core Backend

### F1.1 - Authentification Complète

**Objectif :** Système d'authentification robuste et sécurisé avec toutes les fonctionnalités standards.

#### Tâche 1.1.1 : Login et Register (Révision) ⚠️
- **Description :** Vérifier et améliorer les endpoints existants
- **Fichiers concernés :** `backend/app/api/v1/auth.py`, `backend/app/core/security.py`
- **Endpoints :**
  - `POST /api/v1/auth/register` - Créer un nouveau compte
  - `POST /api/v1/auth/login` - Se connecter et obtenir un token
- **Critères d'acceptation :**
  - [ ] Validation d'email (format valide)
  - [ ] Validation de mot de passe (min 8 caractères, 1 majuscule, 1 chiffre)
  - [ ] Hachage de mot de passe avec bcrypt
  - [ ] Retour d'un JWT valide après login
  - [ ] Gestion d'erreurs claires (email déjà utilisé, mauvais credentials)
  - [ ] Tests unitaires pour tous les cas (succès + erreurs)
- **Test manuel :**
  ```bash
  # Register
  curl -X POST http://localhost:8000/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"Password123","plan":"starter"}'

  # Login
  curl -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"Password123"}'
  ```

#### Tâche 1.1.2 : Reset de Mot de Passe ❌
- **Description :** Permettre aux utilisateurs de réinitialiser leur mot de passe
- **Fichiers concernés :** Nouveaux fichiers à créer
- **Endpoints à créer :**
  - `POST /api/v1/auth/forgot-password` - Demander un reset (envoie email)
  - `POST /api/v1/auth/reset-password` - Définir nouveau mot de passe avec token
- **Critères d'acceptation :**
  - [ ] Token de reset généré avec expiration (1 heure)
  - [ ] Token stocké en base de données (table `password_reset_tokens`)
  - [ ] Email envoyé avec lien de reset (via SendGrid)
  - [ ] Endpoint de reset valide le token et change le mot de passe
  - [ ] Token invalide/expiré retourne une erreur claire
  - [ ] Tests unitaires complets
- **Modèle à créer :**
  ```python
  class PasswordResetToken(SQLModel, table=True):
      id: int = Field(primary_key=True)
      user_id: int = Field(foreign_key="user.id")
      token: str = Field(unique=True, index=True)
      expires_at: datetime
      used: bool = False
  ```

#### Tâche 1.1.3 : Vérification d'Email ❌
- **Description :** Obliger les utilisateurs à vérifier leur email
- **Fichiers concernés :** Nouveaux fichiers + modification de `User` model
- **Endpoints à créer :**
  - `POST /api/v1/auth/send-verification-email` - Renvoyer l'email de vérification
  - `POST /api/v1/auth/verify-email` - Vérifier l'email avec token
- **Critères d'acceptation :**
  - [ ] Champ `email_verified: bool` ajouté au modèle User
  - [ ] Token de vérification généré à l'inscription
  - [ ] Email de vérification envoyé automatiquement
  - [ ] Certaines actions bloquées si email non vérifié (ex: ajouter >1 concurrent)
  - [ ] Banner dans l'UI si email non vérifié
  - [ ] Tests unitaires complets
- **Migration Alembic à créer :**
  ```bash
  alembic revision --autogenerate -m "Add email_verified to User"
  ```

#### Tâche 1.1.4 : Refresh Token ❌
- **Description :** Permettre de renouveler le token sans se reconnecter
- **Fichiers concernés :** `backend/app/api/v1/auth.py`, `backend/app/core/security.py`
- **Endpoints à créer :**
  - `POST /api/v1/auth/refresh` - Obtenir un nouveau access token avec un refresh token
- **Critères d'acceptation :**
  - [ ] Login retourne `access_token` (courte durée : 15 min) + `refresh_token` (longue durée : 7 jours)
  - [ ] Refresh tokens stockés en base (table `refresh_tokens`)
  - [ ] Endpoint /refresh valide le refresh token et retourne un nouveau access token
  - [ ] Refresh tokens peuvent être révoqués (logout)
  - [ ] Tests unitaires complets
- **Modèle à créer :**
  ```python
  class RefreshToken(SQLModel, table=True):
      id: int = Field(primary_key=True)
      user_id: int = Field(foreign_key="user.id")
      token: str = Field(unique=True, index=True)
      expires_at: datetime
      revoked: bool = False
  ```

#### Tâche 1.1.5 : Logout Complet ❌
- **Description :** Révoquer les tokens lors du logout
- **Fichiers concernés :** `backend/app/api/v1/auth.py`
- **Endpoints à créer :**
  - `POST /api/v1/auth/logout` - Révoquer le refresh token actuel
- **Critères d'acceptation :**
  - [ ] Logout marque le refresh token comme `revoked: true`
  - [ ] Access tokens ne peuvent pas être révoqués (courte durée)
  - [ ] Endpoint nécessite authentication
  - [ ] Tests unitaires complets

---

### F1.2 - Gestion des Projets (CRUD Complet)

**Objectif :** Permettre aux utilisateurs de créer et gérer plusieurs projets (workspaces).

#### Tâche 1.2.1 : GET Projects (Révision) ⚠️
- **Description :** Vérifier l'endpoint existant
- **Fichiers concernés :** `backend/app/api/v1/projects.py`
- **Endpoint :** `GET /api/v1/projects/`
- **Critères d'acceptation :**
  - [ ] Retourne uniquement les projets de l'utilisateur connecté
  - [ ] Inclut le nombre de concurrents par projet
  - [ ] Pagination si >20 projets
  - [ ] Tests unitaires

#### Tâche 1.2.2 : POST Project - Créer un Projet ❌
- **Description :** Créer un nouveau projet
- **Endpoint :** `POST /api/v1/projects/`
- **Critères d'acceptation :**
  - [ ] Validation du nom (non vide, max 100 caractères, unique par utilisateur)
  - [ ] Description optionnelle (max 500 caractères)
  - [ ] Vérifier les quotas (Starter: 1 projet, Growth: 5 projets, Ultimate: illimité)
  - [ ] Retourne le projet créé avec son ID
  - [ ] Tests unitaires
- **Body de la requête :**
  ```json
  {
    "name": "Agences Immobilières Paris",
    "description": "Surveillance des concurrents directs"
  }
  ```

#### Tâche 1.2.3 : PATCH Project - Modifier un Projet ❌
- **Description :** Modifier le nom/description d'un projet
- **Endpoint :** `PATCH /api/v1/projects/{project_id}`
- **Critères d'acceptation :**
  - [ ] Vérifier que le projet appartient à l'utilisateur
  - [ ] Permettre la modification partielle (nom seul ou description seule)
  - [ ] Validation des données
  - [ ] Tests unitaires

#### Tâche 1.2.4 : DELETE Project - Supprimer un Projet ❌
- **Description :** Supprimer un projet et tous ses concurrents
- **Endpoint :** `DELETE /api/v1/projects/{project_id}`
- **Critères d'acceptation :**
  - [ ] Vérifier que le projet appartient à l'utilisateur
  - [ ] Suppression en cascade des concurrents et événements (ou soft delete)
  - [ ] Confirmation nécessaire dans le frontend
  - [ ] Tests unitaires

---

### F1.3 - Gestion des Concurrents (CRUD Complet)

**Objectif :** Interface complète pour gérer les concurrents suivis.

#### Tâche 1.3.1 : GET Competitors (Révision) ⚠️
- **Description :** Vérifier et améliorer l'endpoint existant
- **Fichiers concernés :** `backend/app/api/v1/competitors.py`
- **Endpoint :** `GET /api/v1/competitors/?project_id={id}`
- **Critères d'acceptation :**
  - [ ] Filtre par project_id obligatoire
  - [ ] Inclut le nombre d'événements récents (30 jours)
  - [ ] Tri par threat_score par défaut (DESC)
  - [ ] Pagination (limit/offset)
  - [ ] Tests unitaires

#### Tâche 1.3.2 : POST Competitor - Ajouter Manuellement ❌
- **Description :** Créer un endpoint pour ajouter un concurrent manuellement
- **Endpoint :** `POST /api/v1/competitors/`
- **Critères d'acceptation :**
  - [ ] Vérifier les quotas (3/15/50 selon le plan)
  - [ ] Valider les données (nom, URL optionnelle)
  - [ ] Lancer automatiquement une tâche de scraping
  - [ ] Retourner l'ID du concurrent et l'ID de la tâche
  - [ ] WebSocket notification quand le scraping est terminé
  - [ ] Tests unitaires
- **Body de la requête :**
  ```json
  {
    "project_id": 1,
    "name": "Concurrent ABC",
    "url": "https://example.com",
    "auto_scan": true
  }
  ```

#### Tâche 1.3.3 : PATCH Competitor - Modifier ❌
- **Description :** Modifier les informations d'un concurrent
- **Endpoint :** `PATCH /api/v1/competitors/{competitor_id}`
- **Critères d'acceptation :**
  - [ ] Modifier nom, URL, tracking_enabled
  - [ ] Ne pas permettre de modifier le threat_score manuellement
  - [ ] Tests unitaires

#### Tâche 1.3.4 : DELETE Competitor - Supprimer ❌
- **Description :** Supprimer un concurrent
- **Endpoint :** `DELETE /api/v1/competitors/{competitor_id}`
- **Critères d'acceptation :**
  - [ ] Suppression en cascade des événements (ou soft delete)
  - [ ] Tests unitaires

#### Tâche 1.3.5 : POST Refresh Competitor (Révision) ⚠️
- **Description :** Améliorer l'endpoint de refresh manuel
- **Endpoint :** `POST /api/v1/competitors/{id}/refresh`
- **Critères d'acceptation :**
  - [ ] Vérifier les limites de refresh (rate limiting)
  - [ ] Retourner task_id pour suivre la progression
  - [ ] Notifier via WebSocket quand terminé
  - [ ] Tests unitaires

---

### F1.4 - Système de Scoring et d'Événements

**Objectif :** Améliorer la détection et le scoring des événements concurrentiels.

#### Tâche 1.4.1 : Révision du ScoringService ⚠️
- **Description :** Améliorer l'algorithme de calcul du threat_score
- **Fichiers concernés :** `backend/app/services/scoring_service.py`
- **Critères d'acceptation :**
  - [ ] Algorithme documenté et expliqué
  - [ ] Pondération par type d'événement (PRICE: 80, FEATURE: 70, HEALTH: 60, NEW_ENTRANT: 90)
  - [ ] Décroissance temporelle (événements récents pèsent plus)
  - [ ] Tests unitaires avec différents scénarios
- **Formule suggérée :**
  ```python
  score = sum(event.score * decay_factor(days_ago)) / total_events
  decay_factor = exp(-days_ago / 30)  # Décroissance exponentielle
  ```

#### Tâche 1.4.2 : Amélioration de la Détection d'Événements ❌
- **Description :** Utiliser l'IA Gemini pour mieux détecter les événements
- **Fichiers concernés :** `backend/app/services/gemini_service.py`, `backend/app/tasks/analysis_tasks.py`
- **Critères d'acceptation :**
  - [ ] Gemini retourne des événements structurés (type, description, score)
  - [ ] Détection de plusieurs événements par analyse
  - [ ] Metadata enrichie (sentiment, urgence, impact estimé)
  - [ ] Tests avec des données réelles
- **Exemple de réponse Gemini attendue :**
  ```json
  {
    "events": [
      {
        "type": "PRICE",
        "description": "Baisse de 15% sur les services premium",
        "score": 85,
        "metadata": {
          "sentiment": "negative_for_us",
          "urgency": "high",
          "estimated_impact": "Peut capturer 20% de notre clientèle premium"
        }
      }
    ]
  }
  ```

#### Tâche 1.4.3 : Endpoints pour les Événements ⚠️
- **Description :** Améliorer les endpoints existants
- **Endpoints :**
  - `GET /api/v1/competitors/{id}/events` - Liste des événements d'un concurrent
  - `GET /api/v1/events/?project_id={id}` - Tous les événements d'un projet (timeline)
- **Critères d'acceptation :**
  - [ ] Filtres : par type, par date, par score minimum
  - [ ] Tri par date (DESC)
  - [ ] Pagination
  - [ ] Tests unitaires

---

### F1.5 - Système de Notifications

**Objectif :** Envoyer des notifications réelles via email, SMS, Slack, webhook.

#### Tâche 1.5.1 : Configuration SendGrid (Email) ❌
- **Description :** Intégrer SendGrid pour l'envoi d'emails
- **Fichiers concernés :** `backend/app/services/notification_service.py`, `.env`
- **Critères d'acceptation :**
  - [ ] SENDGRID_API_KEY configurée dans .env
  - [ ] Template d'email pour les alertes (HTML + Plain text)
  - [ ] Envoi d'email de test réussi
  - [ ] Gestion d'erreurs (SendGrid down, quota dépassé)
  - [ ] Tests unitaires avec mock
- **Types d'emails :**
  - Email de vérification
  - Reset de mot de passe
  - Alerte d'événement (score > 70)
  - Résumé quotidien (si activé)

#### Tâche 1.5.2 : Integration Slack Webhook ❌
- **Description :** Envoyer des messages dans un channel Slack
- **Fichiers concernés :** `backend/app/services/notification_service.py`
- **Critères d'acceptation :**
  - [ ] Utilisateur peut configurer son webhook Slack dans settings
  - [ ] Messages formatés avec Slack Blocks (rich formatting)
  - [ ] Envoi de test réussi
  - [ ] Gestion d'erreurs
  - [ ] Tests unitaires
- **Format du message :**
  ```
  🚨 *Alerte Concurrent - Vigilux*

  *Concurrent:* Agence XYZ
  *Événement:* Baisse de prix de 15%
  *Score:* 85/100
  *Détails:* [Voir sur Vigilux](https://app.vigilux.com/competitors/123)
  ```

#### Tâche 1.5.3 : Integration Twilio (SMS) ❌
- **Description :** Envoyer des SMS pour les alertes critiques (Ultimate plan uniquement)
- **Fichiers concernés :** `backend/app/services/notification_service.py`, `.env`
- **Critères d'acceptation :**
  - [ ] TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER configurés
  - [ ] Utilisateur peut ajouter son numéro dans settings
  - [ ] SMS envoyé uniquement pour score > 80
  - [ ] Limite de 10 SMS/mois par utilisateur (éviter spam)
  - [ ] Tests unitaires
- **Format SMS :**
  ```
  [Vigilux] Alerte: Concurrent "Agence XYZ" - Baisse de prix 15% (Score: 85). Voir: vigilux.com/c/123
  ```

#### Tâche 1.5.4 : Webhooks Génériques ❌
- **Description :** Permettre l'envoi vers n'importe quelle URL (Zapier, Make, etc.)
- **Fichiers concernés :** `backend/app/services/notification_service.py`
- **Critères d'acceptation :**
  - [ ] Utilisateur peut configurer une URL de webhook
  - [ ] POST JSON vers l'URL lors d'événements
  - [ ] Retry automatique en cas d'échec (3 tentatives)
  - [ ] Signature HMAC pour sécuriser (vérifier authenticité)
  - [ ] Tests unitaires
- **Payload envoyé :**
  ```json
  {
    "event_type": "competitor_event",
    "timestamp": "2024-01-15T10:30:00Z",
    "data": {
      "competitor_id": 123,
      "competitor_name": "Agence XYZ",
      "event_type": "PRICE",
      "description": "Baisse de prix de 15%",
      "score": 85
    },
    "signature": "sha256=abc123..."
  }
  ```

#### Tâche 1.5.5 : Logique de Dispatch ⚠️
- **Description :** Décider quand envoyer quelles notifications
- **Fichiers concernés :** `backend/app/tasks/analysis_tasks.py`
- **Critères d'acceptation :**
  - [ ] Notifications envoyées après création d'un événement
  - [ ] Respecter les préférences utilisateur (email_enabled, sms_enabled, etc.)
  - [ ] Throttling : max 1 notification/heure par concurrent (éviter spam)
  - [ ] Résumé quotidien : agrégation des événements du jour envoyée à 18h
  - [ ] Tests unitaires

---

## PHASE 2 : Fonctionnalités Core Frontend

### F2.1 - Authentification Frontend

**Objectif :** Interface utilisateur complète pour l'authentification.

#### Tâche 2.1.1 : Pages Login et Register (Révision) ⚠️
- **Description :** Améliorer les pages existantes
- **Fichiers concernés :** `frontend/app/login/page.tsx`, `frontend/app/register/page.tsx`
- **Critères d'acceptation :**
  - [ ] Validation côté client (Zod)
  - [ ] Messages d'erreur clairs
  - [ ] Loading states pendant les requêtes
  - [ ] Redirection automatique après login
  - [ ] Remember me (optionnel)
  - [ ] Tests E2E avec Playwright

#### Tâche 2.1.2 : Page Forgot Password ❌
- **Description :** Créer la page de demande de reset
- **Fichier :** `frontend/app/forgot-password/page.tsx`
- **Critères d'acceptation :**
  - [ ] Formulaire avec champ email
  - [ ] Appel API /auth/forgot-password
  - [ ] Message de confirmation affiché
  - [ ] Tests E2E

#### Tâche 2.1.3 : Page Reset Password ❌
- **Description :** Créer la page de reset avec token
- **Fichier :** `frontend/app/reset-password/[token]/page.tsx`
- **Critères d'acceptation :**
  - [ ] Token extrait de l'URL
  - [ ] Formulaire nouveau mot de passe + confirmation
  - [ ] Validation (mots de passe identiques)
  - [ ] Appel API /auth/reset-password
  - [ ] Redirection vers login après succès
  - [ ] Gestion du token invalide/expiré
  - [ ] Tests E2E

#### Tâche 2.1.4 : Email Verification Banner ❌
- **Description :** Afficher un banner si email non vérifié
- **Fichier :** `frontend/components/EmailVerificationBanner.tsx`
- **Critères d'acceptation :**
  - [ ] Banner affiché en haut du dashboard
  - [ ] Bouton "Renvoyer l'email"
  - [ ] Disparaît une fois email vérifié
  - [ ] Tests unitaires

#### Tâche 2.1.5 : AuthContext - Amélioration ⚠️
- **Description :** Améliorer la gestion de l'authentification
- **Fichiers concernés :** `frontend/contexts/AuthContext.tsx`
- **Critères d'acceptation :**
  - [ ] Gestion du refresh token
  - [ ] Auto-refresh avant expiration de l'access token
  - [ ] Logout automatique si refresh échoue
  - [ ] Persist du refresh token dans localStorage (sécurisé)
  - [ ] Tests unitaires

---

### F2.2 - Gestion des Projets Frontend

**Objectif :** Interface pour créer et gérer les projets.

#### Tâche 2.2.1 : Project Selector ❌
- **Description :** Dropdown pour choisir le projet actif
- **Fichier :** `frontend/components/ProjectSelector.tsx`
- **Critères d'acceptation :**
  - [ ] Liste des projets dans un dropdown
  - [ ] Stockage du projet actif dans localStorage
  - [ ] Changement de projet recharge les concurrents
  - [ ] Affichage du nombre de concurrents par projet
  - [ ] Tests unitaires

#### Tâche 2.2.2 : Modal Create Project ❌
- **Description :** Modal pour créer un nouveau projet
- **Fichier :** `frontend/components/modals/CreateProjectModal.tsx`
- **Critères d'acceptation :**
  - [ ] Formulaire nom + description
  - [ ] Validation Zod
  - [ ] Appel POST /api/v1/projects/
  - [ ] Vérification des quotas côté client (message si limite atteinte)
  - [ ] Fermeture et refresh après création
  - [ ] Tests unitaires

#### Tâche 2.2.3 : Modal Edit Project ❌
- **Description :** Modal pour modifier un projet
- **Fichier :** `frontend/components/modals/EditProjectModal.tsx`
- **Critères d'acceptation :**
  - [ ] Formulaire pré-rempli
  - [ ] Appel PATCH /api/v1/projects/{id}
  - [ ] Tests unitaires

#### Tâche 2.2.4 : Delete Project Confirmation ❌
- **Description :** Confirmation avant suppression
- **Fichier :** `frontend/components/modals/DeleteProjectModal.tsx`
- **Critères d'acceptation :**
  - [ ] Modal avec warning (suppression irréversible)
  - [ ] Utilisateur doit taper le nom du projet pour confirmer
  - [ ] Appel DELETE /api/v1/projects/{id}
  - [ ] Redirection vers le premier projet restant
  - [ ] Tests unitaires

---

### F2.3 - Gestion des Concurrents Frontend

**Objectif :** Interface complète pour gérer les concurrents.

#### Tâche 2.3.1 : Activer le Bouton "Add Competitor" ❌
- **Description :** Débloquer et implémenter la fonctionnalité
- **Fichiers concernés :** `frontend/app/dashboard/competitors/page.tsx`, `frontend/components/modals/AddCompetitorModal.tsx`
- **Critères d'acceptation :**
  - [ ] Bouton enabled (enlever disabled et cursor-not-allowed)
  - [ ] Modal avec formulaire (nom, URL optionnelle, auto_scan checkbox)
  - [ ] Vérification des quotas côté client
  - [ ] Appel POST /api/v1/competitors/
  - [ ] Affichage d'un TaskProgress pendant le scraping
  - [ ] Toast notification quand terminé
  - [ ] Tests E2E

#### Tâche 2.3.2 : Edit Competitor ❌
- **Description :** Permettre la modification d'un concurrent
- **Fichier :** `frontend/components/modals/EditCompetitorModal.tsx`
- **Critères d'acceptation :**
  - [ ] Icône "Edit" sur chaque concurrent dans la liste
  - [ ] Modal avec formulaire pré-rempli
  - [ ] Appel PATCH /api/v1/competitors/{id}
  - [ ] Tests E2E

#### Tâche 2.3.3 : Delete Competitor ❌
- **Description :** Supprimer un concurrent
- **Fichier :** `frontend/components/modals/DeleteCompetitorModal.tsx`
- **Critères d'acceptation :**
  - [ ] Icône "Delete" sur chaque concurrent
  - [ ] Confirmation simple (pas besoin de taper le nom)
  - [ ] Appel DELETE /api/v1/competitors/{id}
  - [ ] Tests E2E

#### Tâche 2.3.4 : Amélioration CompetitorList ⚠️
- **Description :** Améliorer l'affichage et les fonctionnalités
- **Fichiers concernés :** `frontend/components/CompetitorList.tsx`
- **Critères d'acceptation :**
  - [ ] Barre de recherche (filtre local sur le nom)
  - [ ] Filtres : par score, par last_scanned_at
  - [ ] Tri : par nom, par score, par date
  - [ ] Pagination côté serveur (si >20 concurrents)
  - [ ] États vides avec illustration et CTA "Add Competitor"
  - [ ] Tests unitaires

---

### F2.4 - Dashboard Analytics

**Objectif :** Visualisations riches et insights.

#### Tâche 2.4.1 : StatCards - Révision ⚠️
- **Description :** Améliorer les cartes de statistiques
- **Fichiers concernés :** `frontend/components/StatCard.tsx`, `frontend/app/dashboard/page.tsx`
- **Critères d'acceptation :**
  - [ ] Icons cohérents avec le thème
  - [ ] Trend indicators (↑ +12% vs last week)
  - [ ] Loading skeletons
  - [ ] Tests unitaires

#### Tâche 2.4.2 : ThreatTimeline - Amélioration ⚠️
- **Description :** Améliorer le graphique de timeline
- **Fichiers concernés :** `frontend/components/ThreatTimeline.tsx`
- **Critères d'acceptation :**
  - [ ] Tooltip riche au hover (liste des événements du jour)
  - [ ] Filtres : par type d'événement
  - [ ] Zoom sur une période spécifique
  - [ ] Export en PNG
  - [ ] Tests unitaires

#### Tâche 2.4.3 : Event Feed - Amélioration ❌
- **Description :** Timeline des événements avec plus de détails
- **Fichiers concernés :** `frontend/components/EventTimeline.tsx`
- **Critères d'acceptation :**
  - [ ] Groupement par date
  - [ ] Icons par type d'événement
  - [ ] Badge de score avec couleur (vert/orange/rouge)
  - [ ] Click pour voir les détails complets (modal)
  - [ ] Infinite scroll ou pagination
  - [ ] Tests unitaires

#### Tâche 2.4.4 : Competitor Comparison ❌
- **Description :** Nouvelle page pour comparer 2+ concurrents côte à côte
- **Fichier :** `frontend/app/dashboard/compare/page.tsx`
- **Critères d'acceptation :**
  - [ ] Sélection de 2-5 concurrents
  - [ ] Tableau comparatif (threat score, nombre d'événements, last scan)
  - [ ] Graphiques comparatifs (superposition des timelines)
  - [ ] Export en PDF
  - [ ] Tests E2E

---

### F2.5 - Radar de Marché

**Objectif :** Scanner de marché et visualisation radar avec vraies données.

#### Tâche 2.5.1 : Backend - Endpoint Radar Metrics ❌
- **Description :** Créer l'endpoint manquant pour les métriques radar
- **Endpoint :** `GET /api/v1/competitors/{id}/radar`
- **Critères d'acceptation :**
  - [ ] Retourne des métriques multi-dimensionnelles réelles :
    - Price Competitiveness (0-100)
    - Innovation (nombre de nouvelles features / temps)
    - Market Presence (avis Google, followers réseaux sociaux)
    - Customer Satisfaction (moyenne des notes)
    - Growth Rate (évolution du nombre d'avis)
  - [ ] Calcul basé sur les données scrapées réelles
  - [ ] Tests unitaires
- **Exemple de réponse :**
  ```json
  {
    "competitor_id": 123,
    "metrics": {
      "price_competitiveness": 75,
      "innovation": 60,
      "market_presence": 85,
      "customer_satisfaction": 90,
      "growth_rate": 70
    },
    "last_updated": "2024-01-15T10:30:00Z"
  }
  ```

#### Tâche 2.5.2 : Frontend - CompetitorRadarChart Amélioration ⚠️
- **Description :** Connecter le radar chart aux vraies données
- **Fichiers concernés :** `frontend/components/CompetitorRadarChart.tsx`
- **Critères d'acceptation :**
  - [ ] Appel GET /api/v1/competitors/{id}/radar
  - [ ] Affichage des vraies métriques (pas de données mockées)
  - [ ] Legend explicative pour chaque axe
  - [ ] Possibilité de comparer plusieurs concurrents sur le même radar
  - [ ] Tests unitaires

#### Tâche 2.5.3 : Market Scan - Amélioration ❌
- **Description :** Améliorer la page de scan de marché
- **Fichiers concernés :** `frontend/app/dashboard/radar/page.tsx`
- **Critères d'acceptation :**
  - [ ] Formulaire de recherche (niche, localisation)
  - [ ] Affichage des résultats en grid cards
  - [ ] Bouton "Track" pour ajouter un concurrent découvert
  - [ ] Vérification des quotas avant d'ajouter
  - [ ] Tests E2E

---

### F2.6 - Settings et Profil Utilisateur

**Objectif :** Permettre à l'utilisateur de gérer son compte et ses préférences.

#### Tâche 2.6.1 : Page Settings - Révision ⚠️
- **Description :** Améliorer la page de settings existante
- **Fichiers concernés :** `frontend/app/dashboard/settings/page.tsx`
- **Critères d'acceptation :**
  - [ ] Tabs : Profile, Notifications, Billing, Security
  - [ ] Tests E2E

#### Tâche 2.6.2 : Tab Profile ❌
- **Description :** Gérer les informations du profil
- **Fichiers concernés :** Nouveau composant
- **Critères d'acceptation :**
  - [ ] Formulaire : email, nom, niche
  - [ ] Changement de mot de passe (ancien + nouveau)
  - [ ] Avatar upload (optionnel)
  - [ ] Bouton "Delete Account" (avec confirmation)
  - [ ] Tests E2E

#### Tâche 2.6.3 : Tab Notifications - Amélioration ⚠️
- **Description :** Améliorer l'UI existante
- **Fichiers concernés :** `frontend/app/dashboard/settings/page.tsx`
- **Critères d'acceptation :**
  - [ ] Toggles clairs pour chaque canal
  - [ ] Input pour webhook URL avec validation
  - [ ] Input pour Slack webhook avec bouton "Test"
  - [ ] Input pour numéro de téléphone (Ultimate plan only)
  - [ ] Fréquence : Instantané vs Résumé quotidien
  - [ ] Tests E2E

#### Tâche 2.6.4 : Tab Billing ❌
- **Description :** Gestion de l'abonnement (après intégration Stripe)
- **Fichiers concernés :** Nouveau composant
- **Critères d'acceptation :**
  - [ ] Affichage du plan actuel + prix
  - [ ] Boutons pour upgrade/downgrade
  - [ ] Historique des paiements
  - [ ] Lien pour gérer le paiement (Stripe Customer Portal)
  - [ ] Annulation d'abonnement
  - [ ] Tests E2E

#### Tâche 2.6.5 : Tab Security ❌
- **Description :** Paramètres de sécurité
- **Fichiers concernés :** Nouveau composant
- **Critères d'acceptation :**
  - [ ] Liste des sessions actives (device, IP, last activity)
  - [ ] Bouton "Logout All Devices"
  - [ ] Enable/Disable 2FA (optionnel pour MVP)
  - [ ] Tests E2E

---

## PHASE 3 : Fonctionnalités Avancées

### F3.1 - Intégration Stripe (Paiement)

**Objectif :** Permettre aux utilisateurs de souscrire et payer leur abonnement.

#### Tâche 3.1.1 : Configuration Stripe ❌
- **Description :** Setup du compte et produits Stripe
- **Critères d'acceptation :**
  - [ ] Compte Stripe créé
  - [ ] 3 produits créés : Starter ($9/mois), Growth ($29/mois), Ultimate ($99/mois)
  - [ ] Webhooks configurés
  - [ ] STRIPE_SECRET_KEY et STRIPE_WEBHOOK_SECRET dans .env
  - [ ] Mode test fonctionnel

#### Tâche 3.1.2 : Backend - Endpoints Stripe ❌
- **Description :** Créer les endpoints pour gérer les abonnements
- **Endpoints à créer :**
  - `POST /api/v1/billing/create-checkout-session` - Créer une session de paiement
  - `POST /api/v1/billing/create-portal-session` - Accès au portail client
  - `POST /api/v1/webhooks/stripe` - Recevoir les webhooks Stripe
- **Critères d'acceptation :**
  - [ ] Checkout session redirige vers Stripe
  - [ ] Webhooks mettent à jour le plan utilisateur en BDD
  - [ ] Gestion des cas : payment_succeeded, subscription_canceled, etc.
  - [ ] Tests unitaires avec Stripe CLI

#### Tâche 3.1.3 : Frontend - Flow de Paiement ❌
- **Description :** Intégrer le flow de paiement dans l'UI
- **Fichiers concernés :** `frontend/app/dashboard/settings/page.tsx`, nouveaux composants
- **Critères d'acceptation :**
  - [ ] Bouton "Upgrade" ouvre le Checkout Stripe
  - [ ] Redirection vers success/cancel pages
  - [ ] Mise à jour du plan en temps réel après paiement
  - [ ] Tests E2E

---

### F3.2 - Monitoring et Observabilité

**Objectif :** Détecter et résoudre les problèmes en production.

#### Tâche 3.2.1 : Integration Sentry ❌
- **Description :** Ajouter le tracking d'erreurs
- **Fichiers concernés :** Backend et Frontend
- **Critères d'acceptation :**
  - [ ] Sentry DSN configuré (.env)
  - [ ] Toutes les exceptions non gérées remontées
  - [ ] Source maps uploadées (pour tracer les erreurs JS)
  - [ ] Environnement taggé (dev/staging/prod)
  - [ ] Tests avec erreur volontaire

#### Tâche 3.2.2 : Structured Logging ❌
- **Description :** Ajouter des logs structurés (JSON)
- **Fichiers concernés :** `backend/app/core/logging.py`
- **Critères d'acceptation :**
  - [ ] Tous les logs au format JSON
  - [ ] Contexte inclus (user_id, request_id, etc.)
  - [ ] Levels appropriés (DEBUG, INFO, WARNING, ERROR)
  - [ ] Rotation des logs
  - [ ] Tests

#### Tâche 3.2.3 : Health Checks ❌
- **Description :** Endpoints pour vérifier la santé des services
- **Endpoints à créer :**
  - `GET /health` - Health check simple (200 OK)
  - `GET /health/detailed` - Vérifie DB, Redis, Celery
- **Critères d'acceptation :**
  - [ ] /health répond en <100ms
  - [ ] /health/detailed vérifie toutes les dépendances
  - [ ] Utilisable par les load balancers
  - [ ] Tests

---

### F3.3 - Tests et Qualité

**Objectif :** Augmenter la couverture de tests et la confiance dans le code.

#### Tâche 3.3.1 : Backend Tests - Augmentation Couverture ⚠️
- **Description :** Atteindre 80% de couverture
- **Fichiers concernés :** `backend/tests/`
- **Critères d'acceptation :**
  - [ ] Tests pour tous les endpoints
  - [ ] Tests pour tous les services
  - [ ] Tests pour les tâches Celery
  - [ ] Coverage report généré automatiquement
  - [ ] CI échoue si coverage < 70%

#### Tâche 3.3.2 : Frontend Tests - Augmentation ⚠️
- **Description :** Tester les composants critiques
- **Fichiers concernés :** `frontend/__tests__/`
- **Critères d'acceptation :**
  - [ ] Tests pour tous les composants UI réutilisables
  - [ ] Tests pour les hooks personnalisés
  - [ ] Tests pour AuthContext
  - [ ] Coverage > 60%

#### Tâche 3.3.3 : E2E Tests - Parcours Complets ❌
- **Description :** Tester les user flows critiques
- **Fichiers concernés :** `e2e/tests/`
- **Critères d'acceptation :**
  - [ ] Test : Register → Login → Add Competitor → View Dashboard
  - [ ] Test : Forgot Password → Reset
  - [ ] Test : Create Project → Add Competitor → Delete Project
  - [ ] Test : Change Notification Settings
  - [ ] CI lance les tests E2E sur chaque PR

#### Tâche 3.3.4 : Load Testing ❌
- **Description :** Tester la performance sous charge
- **Outils :** Locust ou k6
- **Critères d'acceptation :**
  - [ ] Script de test pour 100 utilisateurs simultanés
  - [ ] Mesure de la latence (p50, p95, p99)
  - [ ] Identification des bottlenecks
  - [ ] Documentation des résultats

---

## PHASE 4 : Déploiement Production

### F4.1 - Infrastructure

**Objectif :** Déployer l'application en production de manière fiable.

#### Tâche 4.1.1 : Choix de l'Hébergement ❌
- **Description :** Décider où héberger l'application
- **Options :**
  - AWS (ECS + RDS + ElastiCache)
  - DigitalOcean (App Platform + Managed DB)
  - Railway (simple, tout-en-un)
  - Render (similaire à Railway)
- **Critères d'acceptation :**
  - [ ] Comparaison coûts/features documentée
  - [ ] Décision prise et documentée
  - [ ] Compte créé et configuré

#### Tâche 4.1.2 : Configuration Production ❌
- **Description :** Adapter la configuration pour la prod
- **Fichiers concernés :** `docker-compose.prod.yml`, `.env.production`
- **Critères d'acceptation :**
  - [ ] Variables d'environnement sécurisées (secrets manager)
  - [ ] HTTPS/SSL configuré
  - [ ] Database en managed service (RDS, etc.)
  - [ ] Redis en managed service
  - [ ] Logs envoyés vers un service central
  - [ ] Backups automatiques configurés

#### Tâche 4.1.3 : CI/CD Pipeline Production ❌
- **Description :** Pipeline de déploiement automatique
- **Fichiers concernés :** `.github/workflows/deploy-prod.yml`
- **Critères d'acceptation :**
  - [ ] Déploiement automatique sur merge vers `main`
  - [ ] Environnement de staging déployé sur merge vers `develop`
  - [ ] Smoke tests après déploiement
  - [ ] Rollback automatique si smoke tests échouent
  - [ ] Notifications Slack après déploiement

#### Tâche 4.1.4 : Domain et DNS ❌
- **Description :** Configurer le domaine
- **Critères d'acceptation :**
  - [ ] Domaine acheté (ex: vigilux.com)
  - [ ] DNS configuré (A/CNAME records)
  - [ ] SSL certificate installé (Let's Encrypt)
  - [ ] Redirections http → https
  - [ ] Subdomain pour API (api.vigilux.com)

---

### F4.2 - Sécurité Production

#### Tâche 4.2.1 : Rate Limiting ❌
- **Description :** Protéger contre les abus
- **Outils :** slowapi ou Redis-based rate limiting
- **Critères d'acceptation :**
  - [ ] Limites par endpoint : 100 req/min pour /auth/login, 1000 req/min pour les autres
  - [ ] Limites par IP
  - [ ] Headers de rate limit dans les réponses
  - [ ] Tests

#### Tâche 4.2.2 : CORS Configuration ❌
- **Description :** Configurer CORS de manière sécurisée
- **Fichiers concernés :** `backend/app/main.py`
- **Critères d'acceptation :**
  - [ ] CORS limité au domaine frontend uniquement
  - [ ] Pas de wildcard (*) en production
  - [ ] Tests

#### Tâche 4.2.3 : Security Headers ❌
- **Description :** Ajouter les headers de sécurité recommandés
- **Critères d'acceptation :**
  - [ ] X-Content-Type-Options: nosniff
  - [ ] X-Frame-Options: DENY
  - [ ] Content-Security-Policy configurée
  - [ ] Strict-Transport-Security (HSTS)
  - [ ] Tests avec securityheaders.com

#### Tâche 4.2.4 : Audit de Sécurité ❌
- **Description :** Vérification complète de la sécurité
- **Critères d'acceptation :**
  - [ ] Scan de vulnérabilités des dépendances (npm audit, safety)
  - [ ] Test de penetration basique
  - [ ] Review du code pour injections SQL, XSS, CSRF
  - [ ] Documentation des risques résiduels

---

## PHASE 5 : Post-Launch et Améliorations

### F5.1 - Analytics et Metrics

#### Tâche 5.1.1 : Google Analytics ❌
- **Description :** Tracker l'utilisation de l'application
- **Critères d'acceptation :**
  - [ ] GA4 configuré
  - [ ] Events personnalisés (add_competitor, refresh_competitor, etc.)
  - [ ] Funnels d'acquisition trackés
  - [ ] Tests

#### Tâche 5.1.2 : Product Analytics ❌
- **Description :** Analytics avancées (Mixpanel, PostHog, etc.)
- **Critères d'acceptation :**
  - [ ] Outil choisi et configuré
  - [ ] Tous les events importants trackés
  - [ ] Cohorts d'utilisateurs définis
  - [ ] Dashboards créés

---

### F5.2 - Features Avancées

#### Tâche 5.2.1 : Team Collaboration ❌
- **Description :** Permettre plusieurs utilisateurs par projet
- **Critères d'acceptation :**
  - [ ] Modèle Team et TeamMember
  - [ ] Rôles : Owner, Admin, Editor, Viewer
  - [ ] Invitations par email
  - [ ] Gestion des permissions

#### Tâche 5.2.2 : AI Recommendations ❌
- **Description :** Recommandations stratégiques par l'IA
- **Critères d'acceptation :**
  - [ ] Endpoint qui analyse tous les événements récents
  - [ ] Gemini génère des recommandations stratégiques
  - [ ] Affichage dans un widget Dashboard
  - [ ] Tests

#### Tâche 5.2.3 : Reports Export ❌
- **Description :** Générer des rapports PDF/Excel
- **Critères d'acceptation :**
  - [ ] Export PDF avec graphiques
  - [ ] Export CSV des données brutes
  - [ ] Programmation de rapports récurrents (weekly, monthly)
  - [ ] Tests

---

## Priorités et Ordre d'Exécution Recommandé

### Sprint 1 (2 semaines) - Infrastructure et Auth
1. F0.1 - Configuration Environnement
2. F0.2 - GitHub CI/CD
3. F0.3 - Base de données
4. F1.1 - Authentification complète

### Sprint 2 (2 semaines) - CRUD Complet
5. F1.2 - Gestion Projets
6. F1.3 - Gestion Concurrents
7. F2.2 - Projets Frontend
8. F2.3 - Concurrents Frontend (débloquer Add)

### Sprint 3 (2 semaines) - Notifications et Scoring
9. F1.4 - Scoring et Événements
10. F1.5 - Notifications (Email au minimum)
11. F2.1 - Auth Frontend complète
12. F2.6 - Settings Frontend

### Sprint 4 (2 semaines) - Dashboard et Radar
13. F2.4 - Dashboard Analytics
14. F2.5 - Radar avec vraies données
15. F3.3 - Tests (augmentation couverture)

### Sprint 5 (2 semaines) - Production Ready
16. F3.2 - Monitoring (Sentry)
17. F4.1 - Infrastructure Production
18. F4.2 - Sécurité Production

### Sprint 6 (2 semaines) - Paiement et Launch
19. F3.1 - Stripe Integration
20. F5.1 - Analytics
21. Beta Launch !

---

## Conclusion

Ce roadmap détaille toutes les fonctionnalités nécessaires pour faire de Vigilux un produit complet et production-ready. L'approche incrémentale garantit que chaque fonctionnalité est testée et fonctionnelle avant de passer à la suivante.

**Prochaine étape :** Commencer par la Phase 0 pour mettre en place des bases solides !
