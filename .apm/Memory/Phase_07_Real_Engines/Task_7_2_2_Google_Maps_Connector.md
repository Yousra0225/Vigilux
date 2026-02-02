# Task 7.2.2 - Google Maps Connector

## Status
Completed

## Implementation Details
- **Method Added**: `scrape_google_maps(name: str, location: str)` in `ApifyService`.
- **Actor Used**: `compass/google-maps-scraper`.
- **Configuration**:
  - `searchStrings`: `[f"{name} {location}"]`
  - `maxReviews`: 20 (default for cost/time balance).
  - `exportPlaceUrls`: `True`.
- **Error Handling**: Catches exceptions and returns an empty list to prevent pipeline breakage, with detailed logging.

## Technical Decisions
- Integrated directly into `ApifyService` to leverage the existing `run_actor` method.
- Chose `compass/google-maps-scraper` as the default actor for robust Google Maps data extraction.
- Limited reviews to 20 to ensure reasonably fast execution times.

## Next Steps
- Implement **Task 7.2.3 - Normalization Logic** to process the raw output from this connector.
