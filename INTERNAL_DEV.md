# INTERNAL DEVELOPER DOCUMENTATION

**📌 Ce document est destiné au repository privé uniquement.**

Documentation technique détaillée pour les développeurs ayant accès complet au projet Vigilux.

---

## Table des Matières

1. [Architecture Détaillée](#architecture-détaillée)
2. [État du Projet - Détails Techniques](#état-du-projet)
3. [Problèmes Connus et Solutions](#problèmes-connus)
4. [Décisions d'Architecture](#décisions-darchitecture)
5. [Performance et Optimisation](#performance-et-optimisation)
6. [Sécurité - Points d'Attention](#sécurité)
7. [Debugging et Troubleshooting](#debugging)
8. [Déploiement](#déploiement)

---

## Architecture Détaillée

### Flow Complet: Scraping d'un Concurrent

```
1. User clique "Refresh Competitor" (Frontend)
   ↓
2. POST /api/v1/competitors/{id}/refresh (FastAPI)
   ↓
3. QuotaService.check_refresh_limit(user, competitor)
   - Vérifie le rate limit selon le plan
   - Starter: 1 refresh/heure
   - Growth: 1 refresh/30min
   - Ultimate: 1 refresh/15min
   ↓
4. Task Celery créée: scrape_competitor_task.delay(competitor_id)
   - Task ID retourné au frontend
   ↓
5. API publie sur Redis: "task_started" → WebSocket → Frontend affiche loader
   ↓
6. Celery Worker exécute la tâche:
   a. ApifyService.scrape_google_maps(competitor.name)
      - Lance actor Apify (30-60 secondes)
      - Retry 3x si échec (exponential backoff)
   b. NormalizationService.transform(raw_data)
      - Standardise les données (reviews, rating, etc.)
   c. GeminiService.analyze(normalized_data)
      - Appel API Gemini (3-5 secondes)
      - Prompt: "Analyze competitor and detect events..."
   d. Create Events in DB
      - Parse la réponse Gemini
      - Créer Event objects (type, score, description)
   e. Update Competitor.threat_score
      - ScoringService.calculate_score(events)
   ↓
7. Celery publie sur Redis: "task_completed" → WebSocket → Frontend
   ↓
8. Frontend reçoit notification:
   - Affiche toast: "Competitor updated!"
   - Refresh la liste des competitors
   - Affiche nouveaux événements dans la timeline
```

### Celery Tasks - Détails

**scrape_competitor_task(competitor_id)**
- Durée: 40-90 secondes (dépend d'Apify)
- Max retries: 3
- Retry delay: 60s, 120s, 240s (exponential)
- Exceptions handled:
  - `ApifyActorTimeoutError` → retry
  - `ApifyRateLimitError` → retry après 300s
  - `GeminiAPIError` → log + continue (pas de events créés)

**analyze_competitor_task(competitor_id, scraped_data)**
- Durée: 3-8 secondes
- Max retries: 2
- Utilisé pour analyses asynchrones sans scraping

**perform_market_scan(user_id, niche, location)**
- Durée: 2-5 minutes
- Pas de retry (trop long)
- Retourne liste de nouveaux concurrents potentiels

**run_tiered_scheduler()**
- Celery Beat: schedule périodique
- Ultimate: cron("0 9 * * *")  # 9h tous les jours
- Growth: cron("0 9 * * 1")    # 9h tous les lundis
- Starter: N/A (manuel seulement)

---

## État du Projet - Détails Techniques

### Ce qui Fonctionne ✅

**Backend**
- ✅ JWT Authentication avec bcrypt (30 min token expiry)
- ✅ PostgreSQL avec 5 tables (User, Project, Competitor, Event, NotificationSetting)
- ✅ Celery + Redis pour async tasks
- ✅ WebSocket avec Redis Pub/Sub (socket.io côté client, FastAPI raw WebSocket)
- ✅ Apify scraping (Google Maps actor: dtrungtin/google-maps-scraper)
- ✅ Docker Compose avec 7 services (db, redis, api, worker, beat, flower, web)
- ✅ Alembic migrations (8 migrations au total)

**Frontend**
- ✅ Next.js 14 App Router avec TypeScript
- ✅ AuthContext avec JWT storage dans localStorage
- ✅ WebSocket hook avec auto-reconnect (max 5 retries)
- ✅ React Query pour cache API (staleTime: 5min)
- ✅ Recharts pour timeline (30 jours de data)
- ✅ Tailwind + Shadcn/ui pour styling
- ✅ Dark mode avec next-themes

### Ce qui est Cassé / Incomplet ⚠️

**Backend - Bugs Critiques**
1. **SECRET_KEY hardcodé** (ligne 25 de config.py) - CORRIGÉ dans commit dbda408
2. **Gemini API key non configurée** → Analyse IA ne fonctionne pas
   - Fichier: `backend/app/services/gemini_service.py`
   - Fix: Ajouter `GEMINI_API_KEY` dans `.env`
3. **Notification dispatch est stub** → Emails/SMS non envoyés
   - Fichier: `backend/app/services/notification_service.py:_notify_users_of_insights()`
   - TODO: Implémenter vraiment SendGrid, Twilio, Slack

**Backend - Features Incomplètes**
1. **Project CRUD incomplet** → Manque POST, PATCH, DELETE
   - Fichier: `backend/app/api/v1/projects.py`
   - Ligne 20: Seulement GET implémenté
2. **Radar metrics endpoint manquant** → `/api/v1/competitors/{id}/radar`
   - Frontend appelle cet endpoint mais il n'existe pas
   - Données radar actuelles = synthétiques (dérivées de threat_score)
3. **Rate limiting absent** → Pas de protection contre abus
   - TODO: Ajouter slowapi ou Redis-based rate limiting
4. **CORS origins** → Hardcodé à localhost
   - Production: doit être configuré dynamiquement

**Frontend - Bugs Critiques**
1. **"Add Competitor" button désactivé**
   - Fichier: `frontend/app/dashboard/competitors/page.tsx`
   - Ligne 45: `disabled={true}` + `cursor-not-allowed`
   - Raison: Backend endpoint POST /competitors/ pas testé
2. **WebSocket reconnexion lente** → 5-10s après disconnect
   - Fichier: `frontend/hooks/useWebSocket.ts`
   - Problème: Retry delay trop élevé + pas de heartbeat
3. **Radar chart données mockées**
   - Fichier: `frontend/components/CompetitorRadarChart.tsx`
   - Ligne 30-40: Données hardcodées au lieu d'appel API

**Frontend - UX Issues**
1. Pas de search/filter sur competitors list
2. Pas de pagination (limite à 50 items)
3. Toast notifications parfois dupliquées
4. Loading skeletons manquants sur certaines pages

### Tests - Coverage Actuel

**Backend**
- Coverage: ~35% (estimé)
- Tests existants:
  - ✅ `tests/test_auth.py` (login, register)
  - ✅ `tests/test_services.py` (QuotaService, ScoringService)
  - ⚠️ `tests/test_tasks.py` (minimal, pas de mocks Apify)
- Tests manquants:
  - ❌ API endpoints (competitors, projects, dashboard)
  - ❌ WebSocket connections
  - ❌ Celery tasks avec mocks

**Frontend**
- Coverage: ~20% (estimé)
- Tests existants:
  - ⚠️ `__tests__/components/` (quelques composants)
- Tests manquants:
  - ❌ Pages complètes
  - ❌ Hooks (useWebSocket, useAuth)
  - ❌ Context (AuthContext)

**E2E**
- Framework: Playwright configuré
- Tests: 0 (aucun test E2E écrit)

---

## Problèmes Connus et Solutions

### 1. WebSocket Déconnexion Fréquente

**Symptôme**: Frontend perd la connexion WS toutes les 2-3 minutes

**Cause**: Pas de heartbeat/ping-pong pour garder la connexion alive

**Solution**:
```typescript
// frontend/hooks/useWebSocket.ts
useEffect(() => {
  const interval = setInterval(() => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: 'ping' }));
    }
  }, 30000); // Ping toutes les 30s

  return () => clearInterval(interval);
}, []);
```

```python
# backend/app/api/v1/notifications.py
@app.websocket("/api/v1/notifications/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    # ... existing code ...
    async for message in websocket.iter_text():
        data = json.loads(message)
        if data.get('type') == 'ping':
            await websocket.send_text(json.dumps({'type': 'pong'}))
```

### 2. Celery Tasks Qui Fail Silencieusement

**Symptôme**: Task Celery échoue mais le frontend ne reçoit aucune notification

**Cause**: Exceptions non catchées + pas de publication Redis sur erreur

**Solution**:
```python
# backend/app/tasks/scraping_tasks.py
@celery_app.task(bind=True, max_retries=3)
def scrape_competitor_task(self, competitor_id: int):
    try:
        # ... existing logic ...
    except Exception as e:
        # Publier l'erreur sur Redis
        redis_client.publish(
            f"notifications:user_{user_id}",
            json.dumps({
                "type": "task_failed",
                "task_id": self.request.id,
                "error": str(e)
            })
        )
        raise  # Re-raise pour Celery retry
```

### 3. Apify Rate Limit Errors

**Symptôme**: `ApifyRateLimitError: Account exceeded monthly usage limit`

**Cause**: Free tier = $5/month (~500 scrapes), facile à dépasser en dev

**Solution temporaire**: Utiliser des données mockées en développement
```python
# backend/app/services/apify_service.py
class ApifyService:
    def scrape_google_maps(self, query: str):
        if settings.ENVIRONMENT == "development" and settings.USE_MOCK_DATA:
            return self._get_mock_data()
        # ... existing Apify logic ...
```

**Solution permanente**: Implémenter un cache Redis des scrapes (TTL: 1 jour)

---

## Décisions d'Architecture

### Pourquoi Celery et pas AWS Lambda / Cloud Functions ?

**Pros Celery**:
- Gratuit (self-hosted)
- Control total sur retry logic
- Flower pour monitoring
- Familiarité avec Python ecosystem

**Cons Celery**:
- Need to manage workers (scaling manual)
- More complex setup vs serverless

**Décision**: Celery pour MVP (< 1000 users), évaluer serverless si croissance > 10k users/month

### Pourquoi PostgreSQL et pas MongoDB ?

**Raisons**:
- Relations claires (User → Project → Competitor → Event)
- ACID transactions nécessaires (paiements futurs)
- SQLModel rend l'ORM agréable (type hints + validation)
- JSON column pour metadata flexible

### Pourquoi FastAPI et pas Django ?

**Raisons**:
- Performance supérieure (async support natif)
- Type hints = auto-documentation (Swagger)
- Plus moderne, moins de boilerplate
- WebSocket support built-in

---

## Performance et Optimisation

### Bottlenecks Identifiés

1. **Apify scraping = 30-60s par competitor**
   - Solution: Batch scraping (scraper plusieurs en parallèle)
   - Celery group: `group([scrape.si(id) for id in ids])()`

2. **Dashboard stats query lente (>500ms si 50+ competitors)**
   - Problème: 3 queries séparées
   - Solution: Single query avec aggregations
   ```sql
   SELECT
     COUNT(*) as total_competitors,
     COUNT(CASE WHEN events.score > 70 THEN 1 END) as breakthroughs,
     AVG(threat_score) as avg_score
   FROM competitors
   LEFT JOIN events ON events.competitor_id = competitors.id
   WHERE competitors.user_id = ?
   ```

3. **Frontend re-renders excessifs**
   - Problème: AuthContext cause full app re-render sur token refresh
   - Solution: useMemo + React.memo sur composants lourds

### Opportunités d'Optimisation

1. **Redis cache pour dashboard stats** (TTL: 5 min)
2. **Pagination côté serveur** (actuellement limite à 50)
3. **Lazy loading des images** (avatars, logos competitors)
4. **Service Worker** pour cacher assets statiques
5. **Database indexes** sur colonnes fréquemment requêtées:
   ```sql
   CREATE INDEX idx_events_competitor_detected ON events(competitor_id, detected_at DESC);
   CREATE INDEX idx_competitors_user_score ON competitors(user_id, threat_score DESC);
   ```

---

## Sécurité - Points d'Attention

### Vulnérabilités Connues

1. **SECRET_KEY par défaut** → CRITIQUE (CORRIGÉ)
   - Status: ✅ Corrigé dans commit dbda408
   - Validator ajouté qui error en production

2. **Pas de rate limiting** → Risque de DDoS/brute force
   - Status: ❌ À faire
   - Impact: HIGH
   - Solution: slowapi ou middleware custom

3. **CORS origins hardcodé** → Risque en production
   - Status: ⚠️ Partiellement traité
   - `.env`: `BACKEND_CORS_ORIGINS='["http://localhost:3000"]'`
   - Production: doit être domaine réel

4. **Pas de CSRF protection** → Risque pour API mutations
   - Status: ❌ À faire
   - Impact: MEDIUM
   - Solution: Double submit cookie pattern

5. **JWT tokens non révocables** → User logout inefficace
   - Status: ❌ À faire (dans ROADMAP: Tâche 1.1.4)
   - Solution: Refresh tokens avec database storage

6. **SQL Injection potentielle** → SQLModel protège, mais queries raw existent
   - Status: ⚠️ À auditer
   - Fichiers à vérifier: `backend/app/api/v1/dashboard.py` (queries custom)

### Checklist Avant Production

- [ ] SECRET_KEY généré aléatoirement
- [ ] Rate limiting activé (100 req/min par IP)
- [ ] CORS origins = domaine production uniquement
- [ ] HTTPS/TLS activé avec certificat valide
- [ ] Helmet.js équivalent pour headers de sécurité
- [ ] Dependencies scan (npm audit, safety check)
- [ ] Penetration testing basique
- [ ] Monitoring d'erreurs (Sentry configuré)
- [ ] Logs structurés (JSON format)
- [ ] Secrets dans secrets manager (AWS/Azure)
- [ ] Database backups automatiques (daily minimum)

---

## Debugging et Troubleshooting

### Logs Utiles

**Celery Worker Logs**:
```bash
docker-compose logs -f worker
# Voir les tasks en cours:
docker-compose exec worker celery -A app.tasks.celery_app inspect active
# Voir les tasks registered:
docker-compose exec worker celery -A app.tasks.celery_app inspect registered
```

**FastAPI Logs**:
```bash
docker-compose logs -f api
# Logs en temps réel avec filtering:
docker-compose logs -f api | grep ERROR
```

**Redis Monitoring**:
```bash
docker-compose exec redis redis-cli MONITOR
# Voir les keys:
docker-compose exec redis redis-cli KEYS "*"
# Voir les channels:
docker-compose exec redis redis-cli PUBSUB CHANNELS
```

**PostgreSQL Debug**:
```bash
docker-compose exec db psql -U vigilux_user -d vigilux
# Voir les queries lentes:
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### Commandes de Debug Courantes

**Reset complet de l'environnement**:
```bash
docker-compose down -v  # Détruit volumes (DATA LOSS!)
docker-compose up --build
docker-compose exec api alembic upgrade head
docker-compose exec api python -m app.db.seed
```

**Tester une task Celery manuellement**:
```bash
docker-compose exec worker python
>>> from app.tasks.scraping_tasks import scrape_competitor_task
>>> result = scrape_competitor_task.delay(1)
>>> result.ready()  # False si en cours
>>> result.get()    # Bloque jusqu'à completion, retourne résultat
```

**Tester l'API sans frontend**:
```bash
# Login et get token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"starter@example.com","password":"password123"}' \
  | jq -r '.access_token')

# Utiliser le token
curl http://localhost:8000/api/v1/competitors/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## Déploiement

### Infrastructure Recommandée

**Option 1: AWS (Scalable)**
- ECS Fargate pour API + Worker
- RDS PostgreSQL (db.t3.micro = $15/mois)
- ElastiCache Redis (cache.t3.micro = $12/mois)
- ALB pour load balancing
- S3 + CloudFront pour frontend
- Total: ~$50/mois

**Option 2: DigitalOcean (Simplicity)**
- App Platform (API + Worker + Frontend)
- Managed PostgreSQL ($15/mois)
- Managed Redis ($15/mois)
- Total: ~$40/mois

**Option 3: Railway (Speed)**
- All-in-one platform
- PostgreSQL + Redis inclus
- Auto-deploy from Git
- Total: ~$25/mois (free tier disponible)

### Variables d'Environnement Production

```env
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql://user:pass@prod-db:5432/vigilux
REDIS_URL=redis://prod-redis:6379/0
SECRET_KEY=<GENERATE_NEW_ONE>
BACKEND_CORS_ORIGINS='["https://vigilux.com"]'
NEXT_PUBLIC_API_URL=https://api.vigilux.com
SENTRY_DSN=https://xxx@sentry.io/xxx
```

### Checklist de Déploiement

**Pré-déploiement**:
- [ ] Tests passent (backend + frontend)
- [ ] Build Docker réussit
- [ ] Migrations testées sur copie de prod DB
- [ ] Variables d'environnement documentées
- [ ] Secrets stockés dans secrets manager

**Post-déploiement**:
- [ ] Smoke tests (login, view dashboard, refresh competitor)
- [ ] Monitoring activé (Sentry, logs)
- [ ] Backups DB vérifiés
- [ ] SSL certificate valide
- [ ] DNS configuré correctement

**Rollback Plan**:
```bash
# Revenir à version précédente
git revert HEAD
docker build -t vigilux-api:rollback .
# Deploy rollback version
```

---

## Contacts et Ressources

**Lead Developer**: Yousra
**Repository Privé**: [À définir après création]
**Documentation Publique**: [GitHub public repo]

**Ressources Externes**:
- Apify Docs: https://docs.apify.com
- Gemini API: https://ai.google.dev/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- Celery Docs: https://docs.celeryq.dev

---

**Dernière mise à jour**: 2026-07-07
**Version**: 0.1.0-alpha
