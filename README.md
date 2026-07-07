# Vigilux - Intelligence Concurrentielle Automatisée

## Qu'est-ce que Vigilux ?

**Vigilux** est une plateforme SaaS qui surveille automatiquement vos concurrents et vous alerte en temps réel des mouvements importants du marché.

Au lieu de passer des heures à analyser manuellement vos concurrents, Vigilux le fait pour vous 24/7 et vous envoie des insights générés par intelligence artificielle.

### Cas d'usage concret

Imaginez que vous êtes une agence immobilière à Paris :
1. Vous ajoutez vos 10 concurrents principaux dans Vigilux
2. Chaque jour, Vigilux scrape leurs données (Google Maps, sites web, etc.)
3. L'IA détecte automatiquement :
   - Changements de prix
   - Nouvelles fonctionnalités/services
   - Nouveaux avis clients (positifs ou négatifs)
   - Nouveaux concurrents qui apparaissent dans votre zone
4. Vous recevez une notification instantanée : "🚨 Concurrent X a baissé ses prix de 15%"
5. Vous consultez le dashboard pour voir l'analyse complète et ajuster votre stratégie

---

## Technologies Utilisées

### Backend
- **FastAPI** (Python) - API REST rapide et moderne
- **PostgreSQL** - Base de données relationnelle pour stocker users, competitors, events
- **Redis** - Utilisé pour :
  - File d'attente des tâches asynchrones
  - Cache des données fréquemment consultées
  - Communication entre services (Pub/Sub)
- **Celery** - Exécution de tâches longues en arrière-plan (scraping, analyse IA)
- **Celery Beat** - Planificateur de tâches récurrentes (scan quotidien pour Ultimate plan)
- **SQLModel** - ORM moderne qui combine SQLAlchemy + Pydantic
- **Alembic** - Gestion des migrations de base de données

### Frontend
- **Next.js 14** (App Router) - Framework React avec rendu côté serveur
- **TypeScript** - JavaScript typé pour éviter les erreurs
- **Tailwind CSS** - Framework CSS utilitaire pour le design
- **Shadcn/ui** - Composants UI pré-construits (buttons, cards, forms)
- **Recharts** - Librairie de graphiques pour les visualisations
- **React Query** - Gestion du cache et des requêtes API
- **Zod** - Validation de formulaires
- **Socket.io Client** - WebSockets pour les mises à jour temps réel

### Services Externes
- **Apify** - Plateforme de web scraping (Google Maps, sites web)
- **Google Gemini AI** - Analyse intelligente des données de concurrents
- **SendGrid** - Envoi d'emails transactionnels et notifications
- **Twilio** - Envoi de SMS pour les alertes critiques

### DevOps
- **Docker** - Conteneurisation de tous les services
- **Docker Compose** - Orchestration de 7 services simultanés
- **GitHub Actions** - CI/CD pour les tests et linting

---

## Architecture Simplifiée

```
┌─────────────────┐
│   Utilisateur   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      WebSocket      ┌──────────────┐
│  Frontend       │◄────────────────────►│   API        │
│  (Next.js)      │      Notifications   │  (FastAPI)   │
└─────────────────┘                      └──────┬───────┘
                                                │
                         ┌──────────────────────┼─────────────────┐
                         │                      │                 │
                         ▼                      ▼                 ▼
                  ┌──────────────┐      ┌─────────────┐   ┌──────────┐
                  │  PostgreSQL  │      │   Redis     │   │  Celery  │
                  │   (Données)  │      │  (Queue)    │   │ (Worker) │
                  └──────────────┘      └─────────────┘   └────┬─────┘
                                                                │
                                        ┌───────────────────────┼────────────┐
                                        │                       │            │
                                        ▼                       ▼            ▼
                                  ┌─────────┐           ┌───────────┐  ┌─────────┐
                                  │  Apify  │           │  Gemini   │  │  Email  │
                                  │(Scraper)│           │    AI     │  │  /SMS   │
                                  └─────────┘           └───────────┘  └─────────┘
```

### Comment ça fonctionne ?

1. **User lance un scan** → Frontend envoie une requête à l'API
2. **API crée une tâche** → Enregistre la tâche dans Redis et répond immédiatement
3. **Celery Worker prend la tâche** → Execute le scraping via Apify (30-60 secondes)
4. **Données normalisées** → Transforme les données brutes en format standardisé
5. **Analyse IA** → Envoie à Gemini pour extraire les insights importants
6. **Création d'événements** → Stocke dans PostgreSQL les changements détectés
7. **Notification en temps réel** → Redis Pub/Sub → API → WebSocket → Frontend affiche un toast

---

## Fonctionnalités Principales

### 1. Gestion des Concurrents
- Ajouter des concurrents manuellement ou via recherche
- Voir la liste de tous les concurrents suivis
- Mettre à jour manuellement un concurrent (refresh)
- Voir le score de menace de chaque concurrent (0-100)
- Voir la dernière date de scan

### 2. Détection d'Événements
Vigilux détecte automatiquement 4 types d'événements :
- **PRICE** : Changement de prix ou offres promotionnelles
- **FEATURE** : Nouvelle fonctionnalité, service, ou produit lancé
- **HEALTH** : Changement d'avis clients (note, commentaires)
- **NEW_ENTRANT** : Nouveau concurrent détecté dans le marché

Chaque événement a :
- Un score d'importance (0-100)
- Une description générée par l'IA
- Un timestamp
- Un type

### 3. Dashboard Analytics
- **Total Competitors** : Nombre de concurrents suivis
- **Breakthroughs** : Événements majeurs (score > 70) dans les 30 derniers jours
- **Average Threat Score** : Score moyen de menace de tous les concurrents
- **Timeline Chart** : Graphique des événements sur 30 jours
- **Recent Events** : Liste chronologique des derniers mouvements

### 4. Radar de Marché
- Scanner automatique de nouveaux concurrents dans votre niche
- Visualisation radar (spider chart) des forces/faiblesses
- Découverte de concurrents dont vous n'aviez pas connaissance

### 5. Notifications Multi-Canaux
Configuration par utilisateur :
- **Email** : Résumé quotidien ou alertes instantanées
- **Webhook** : Envoi vers votre système (Zapier, Make, etc.)
- **Slack** : Messages dans un channel dédié
- **SMS** : Pour les événements critiques (Plan Ultimate uniquement)

### 6. Plans Tarifaires
- **Starter** : 3 concurrents, scan manuel uniquement
- **Starter Plus** : 10 concurrents, scan hebdomadaire
- **Growth** : 25 concurrents, scan quotidien
- **Ultimate** : 50 concurrents, scan quotidien + SMS + support prioritaire

---

## Structure du Projet

```
Vigilux/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── api/            # Routes API (auth, competitors, dashboard, etc.)
│   │   ├── models/         # Modèles SQLModel (User, Competitor, Event, etc.)
│   │   ├── services/       # Logique métier (QuotaService, GeminiService, etc.)
│   │   ├── tasks/          # Tâches Celery (scraping, analysis, scheduling)
│   │   ├── core/           # Config, security, dependencies
│   │   └── main.py         # Point d'entrée FastAPI
│   ├── tests/              # Tests unitaires et d'intégration
│   ├── alembic/            # Migrations de base de données
│   └── requirements.txt    # Dépendances Python
│
├── frontend/               # Application Next.js
│   ├── app/               # Pages (App Router)
│   │   ├── login/
│   │   ├── register/
│   │   └── dashboard/     # Competitors, radar, settings
│   ├── components/        # Composants React réutilisables
│   ├── contexts/          # Context API (AuthContext)
│   ├── hooks/             # Hooks personnalisés (useWebSocket)
│   └── lib/               # Utilitaires (API client, etc.)
│
├── docker-compose.yml     # Orchestration de tous les services
├── .env.example           # Variables d'environnement (template)
└── README.md             # Ce fichier
```

---

## Installation et Lancement

### Prérequis
- Docker et Docker Compose installés
- Git
- (Optionnel) Node.js 18+ et Python 3.11+ pour développement local

### Étapes

1. **Cloner le projet**
```bash
git clone <repo-url>
cd Vigilux
```

2. **Configurer les variables d'environnement**
```bash
cp .env.example .env
# Éditer .env et remplir :
# - APIFY_API_TOKEN (obtenir sur apify.com)
# - GEMINI_API_KEY (obtenir sur ai.google.dev)
# - SECRET_KEY (générer avec : openssl rand -hex 32)
```

3. **Lancer tous les services avec Docker**
```bash
docker-compose up --build
```

Cela démarre :
- PostgreSQL (port 5432)
- Redis (port 6379)
- API FastAPI (port 8000)
- Celery Worker
- Celery Beat (scheduler)
- Flower (monitoring Celery) (port 5555)
- Frontend Next.js (port 3000)

4. **Initialiser la base de données**
```bash
docker-compose exec api alembic upgrade head
```

5. **Créer des utilisateurs de test** (optionnel)
```bash
docker-compose exec api python -m app.db.seed
```

6. **Accéder à l'application**
- Frontend : http://localhost:3000
- API Docs : http://localhost:8000/docs
- Flower (Celery monitoring) : http://localhost:5555

---

## Fonctionnalités Techniques Implémentées

### Architecture & Infrastructure
- **Microservices orchestrés** avec Docker Compose (7 services)
- **Base de données PostgreSQL** avec migrations Alembic
- **Cache & Message Broker** Redis pour performance et communication
- **Async Task Processing** via Celery avec Celery Beat pour scheduling
- **Real-time Communication** avec WebSockets (Redis Pub/Sub)

### Backend (FastAPI)
- **API REST** complète avec documentation Swagger auto-générée
- **Authentification JWT** sécurisée avec bcrypt
- **Service Layer** modulaire (QuotaService, ScoringService, GeminiService, ApifyService)
- **Web Scraping** intégré via Apify pour extraction de données Google Maps
- **AI Analysis** avec Google Gemini pour génération d'insights
- **Rate Limiting** par plan utilisateur (quotas competitors, fréquence refresh)

### Frontend (Next.js 14)
- **App Router** avec Server Components et Client Components
- **TypeScript** pour type safety
- **Real-time Updates** via WebSocket avec reconnexion automatique
- **State Management** avec React Context et React Query
- **UI Components** professionnels (Shadcn/ui + Tailwind CSS)
- **Data Visualization** avec Recharts (timeline, radar charts)
- **Dark Mode** support

### DevOps & Testing
- **GitHub Actions** CI/CD pour tests et linting automatiques
- **Docker** pour environnement reproductible
- **Tests** unitaires et d'intégration (Pytest, Vitest)
- **E2E Testing** setup avec Playwright

---

## Développement

### Backend

**Lancer en mode dev avec hot-reload :**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Créer une migration :**
```bash
alembic revision --autogenerate -m "Description du changement"
alembic upgrade head
```

**Lancer les tests :**
```bash
pytest
```

### Frontend

**Lancer en mode dev :**
```bash
cd frontend
npm install
npm run dev
```

**Build pour production :**
```bash
npm run build
npm start
```

---

## Roadmap

Voir [ROADMAP.md](./ROADMAP.md) pour la liste détaillée des fonctionnalités à développer et leur ordre de priorité.

---

## Support & Contribution

Ce projet est en développement actif. Pour toute question ou contribution :
- Créer une issue sur GitHub
- Contacter l'équipe de développement

---

## Licence

[À définir]
