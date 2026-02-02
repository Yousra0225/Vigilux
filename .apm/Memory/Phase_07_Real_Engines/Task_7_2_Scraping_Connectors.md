# Task 7.2 - Real-world Scraping Connectors (Apify)

## Overview
Integrated Apify's Google Maps Scraper to replace mock data with real market data for competitor discovery. The implementation includes graceful fallback to mock data when Apify credentials are not configured.

## Implementation Details

### 1. Dependencies Added
**File:** `backend/requirements.txt`

Added Apify client library:
```
apify-client>=1.6.0
```

### 2. Configuration
**File:** `backend/app/core/config.py`

Added Apify API token configuration:
```python
APIFY_API_TOKEN: str = ""
```

**File:** `docker-compose.yml`

Added environment variable to `api` and `worker` services:
```yaml
APIFY_API_TOKEN: ${APIFY_API_TOKEN:-}
```

Usage: Set the token in `.env` file or pass via environment:
```bash
export APIFY_API_TOKEN=your_token_here
docker-compose up
```

### 3. Apify Service
**File:** `backend/app/services/apify.py`

Created `ApifyService` class with the following methods:

#### `is_configured()`
Static method to check if Apify token is configured.

#### `search_competitors(query, location, max_results, language)`
Main search method using Apify's Google Maps Scraper actor.

**Parameters:**
- `query`: Search query (e.g., "saas companies", "crm software")
- `location`: Geographic location (optional)
- `max_results`: Maximum results (default: 20)
- `language`: Language code (default: "en")

**Returns:** List of standardized competitor dicts with:
- `name`: Business name
- `url`: Website URL
- `score`: Calculated threat score (0-100)
- `description`: Business description
- `address`: Business address
- `phone`: Phone number
- `rating`: Average rating (if available)
- `review_count`: Number of reviews
- `categories`: List of business categories

#### `_transform_apify_result(item)`
Transforms raw Apify output into standardized format:
- Extracts name, URL, address, phone
- Builds description from categories
- Calculates score from rating and review count

#### `scrape_website(url)`
Bonus method for scraping individual websites using Apify's Website Content Extractor.

#### `_get_client()`
Returns initialized `ApifyClient` or `None` if token not configured.

### 4. Task Integration
**File:** `backend/app/tasks/radar.py`

Updated `perform_market_scan` task with conditional logic:

```python
if ApifyService.is_configured():
    # Use real Apify data
    apify_results = ApifyService.search_competitors(...)
    return transformed_results
else:
    # Fallback to mock data
    logger.info("Using mock data generation")
    return mock_results
```

**New Parameters:**
- `location`: Optional geographic location for targeted searches

### 5. Services Export
**File:** `backend/app/services/__init__.py`

Added `ApifyService` to exports for easy importing.

## Architecture

```
                    ┌─────────────────┐
                    │ perform_market  │
                    │    _scan()      │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  ApifyService   │
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
        ┌───────▼────────┐      ┌────────▼────────┐
        │ APIFY_TOKEN    │      │ APIFY_TOKEN     │
        │    Present     │      │   Missing       │
        └───────┬────────┘      └────────┬────────┘
                │                        │
        ┌───────▼────────┐      ┌───────▼────────┐
        │  Apify API     │      │  Mock Data     │
        │  Google Maps   │      │  Generator     │
        └───────┬────────┘      └───────┬────────┘
                │                        │
                └────────────┬───────────┘
                             │
                    ┌────────▼────────┐
                    │  RadarResult[]  │
                    └─────────────────┘
```

## Scoring Algorithm

The Apify results are scored based on:
1. **Base Score:** 50 points
2. **Rating Bonus:** Up to 30 points (Google rating 1-5 scaled to 0-30)
3. **Review Count Bonus:** Up to 20 points
   - 1000+ reviews: +20 points
   - 100+ reviews: +10 points
   - 10+ reviews: +5 points

Final score is clamped to 0-100 range.

## API Usage

### With Apify Token (Real Data)
```bash
# Set environment variable
export APIFY_API_TOKEN=apify_api_xxxxx

# Restart services
docker-compose up -d

# Trigger scan
GET /api/v1/competitors/radar/scan?query=saas&location=United+States
```

### Without Token (Mock Data - Development)
```bash
# No token needed - uses mock data
GET /api/v1/competitors/radar/scan?query=saas
```

## Apify Actors Used

| Actor | Use Case |
|-------|----------|
| `apify/google-maps-scraper` | Business/competitor discovery |
| `apify/website-content-extractor` | Website scraping (bonus method) |

## Data Flow Example

```
User Request → Celery Task → ApifyService.search_competitors("saas", "US")
                                    ↓
                        ApifyClient.actor("google-maps-scraper")
                                    ↓
                        Actor runs with search parameters
                                    ↓
                        Dataset items fetched and transformed
                                    ↓
                        Standardized results returned
                                    ↓
                        Competitor objects added to project
```

## Benefits

1. **Real Data:** Access to actual business listings via Google Maps
2. **Graceful Degradation:** Falls back to mock data when credentials unavailable
3. **Geographic Targeting:** Support for location-based searches
4. **Rich Metadata:** Ratings, reviews, categories, addresses
5. **Scalable:** Leverages Apify's infrastructure for web scraping

## Success Criteria
- [x] Code successfully initializes the Apify client
- [x] Task logic correctly distinguishes between "real" mode (Apify) and "mock" mode
- [x] Graceful fallback when token is missing
- [x] Results are transformed to standard RadarResult format

## Getting an Apify Token

1. Sign up at https://apify.com/
2. Navigate to Account > API Tokens
3. Create a new token
4. Set as environment variable: `APIFY_API_TOKEN=your_token`

## Future Enhancements
- Add more Apify actors (LinkedIn scraper, Crunchbase scraper)
- Implement caching for Apify results to reduce API calls
- Add retry logic with exponential backoff for Apify failures
- Implement quota management for Apify API usage
- Add ability to scrape individual competitor websites for deeper insights
- Support for custom Apify actors
