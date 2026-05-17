# Plan

## Overall Goal
Build a backend for the MVP of a "budget-first travel finder" web app using FastAPI. The core idea is not to start from a destination, but to generate ready-made vacation scenarios that fit the user's budget and flexible dates.

Main goals:
- Game-like UX on the frontend: very simple input, minimal filters.
- A "Find at any cost" algorithm with cascading fallbacks.
- Deliver prepared travel packages, not just raw flight and hotel lists.
- Work with limited API budget by using caching and preloaded popular destinations.

---

## Backend tasks

1. Set up a FastAPI project following best practices.
2. Design data models for user requests and package responses.
3. Implement a tour search service with fallback logic.
4. Support flexible date input: exact dates, windows, seasons.
5. Add caching for results and a repository of popular destinations.
6. Provide API endpoints for search, package discovery, and status.
7. Include basic logging, monitoring, and error handling.
8. Define JSON response contracts for the frontend.

---

## Project structure

### Recommended structure

```
triper_backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── search.py
│   │   │   │   ├── packages.py
│   │   │   │   └── health.py
│   │   │   └── api_router.py
│   │   └── deps.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── settings.py
│   ├── models/
│   │   ├── requests.py
│   │   ├── responses.py
│   │   └── domain.py
│   ├── services/
│   │   ├── search_service.py
│   │   ├── fallback_engine.py
│   │   ├── cache_service.py
│   │   └── external_adapters.py
│   ├── db/
│   │   ├── repository.py
│   │   ├── seeds.py
│   │   └── schemas.py
│   ├── utils/
│   │   ├── date_utils.py
│   │   ├── money_utils.py
│   │   └── validation.py
│   ├── main.py
│   └── version.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── data_fixtures/
├── Dockerfile
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

### Structure rationale
- `app/api/v1/endpoints/` — HTTP endpoints.
- `app/models/` — Pydantic schemas for requests and responses.
- `app/services/` — business logic, fallback algorithm, cache and external API adapters.
- `app/db/` — storage for popular destinations, offline cache, and seed data.
- `app/core/` — configuration, settings, logging.
- `app/utils/` — helper utilities for dates, money, and validation.

---

## API endpoints

### 1. POST `/api/v1/search`

Description: main endpoint for searching travel packages by budget, dates, and preferences.

Request JSON:

```json
{
  "origin": "Helsinki",
  "travelers": 2,
  "budget": 1000,
  "currency": "USD",
  "date_type": "flexible",
  "date_range": {
    "from": "2025-08-01",
    "to": "2025-08-31"
  },
  "duration": {
    "min_days": 7,
    "max_days": 10
  },
  "preferences": ["sea", "architecture"],
  "mood": "surprise"
}
```

Fields:
- `origin` — departure city.
- `travelers` — number of travelers.
- `budget` — total budget in the chosen currency.
- `currency` — budget currency.
- `date_type` — `exact`, `window`, `seasonal`.
- `date_range` — exact range or flexible window.
- `duration` — preferred trip length.
- `preferences` — optional travel preferences.
- `mood` — optional game-like mode such as `surprise`, `relax`, `budget`.

Response JSON:

```json
{
  "request_id": "abc123",
  "status": "processing",
  "eta_seconds": 5,
  "summary": "We are preparing 4 ready-made holiday options within your budget",
  "packages": []
}
```

If the result is ready immediately, the `packages` array will contain offers.

### 2. GET `/api/v1/search/{request_id}`

Description: retrieve the search result by request ID.

Response JSON:

```json
{
  "request_id": "abc123",
  "status": "completed",
  "duration_seconds": 3,
  "packages": [
    {
      "package_id": "opt-001",
      "title": "Optimal choice: Prague for 7 days",
      "description": "Balanced flight and a good hotel in a popular city",
      "direction": "Prague, Czech Republic",
      "budget_breakdown": {
        "transport": 420,
        "accommodation": 330,
        "activities": 120,
        "buffer": 130
      },
      "total_price": 1000,
      "currency": "USD",
      "days": 7,
      "travel_type": "flight+hotel",
      "transport_summary": "one-stop flight, carry-on only",
      "accommodation_summary": "4-star apartments near the Old Town",
      "fallback_level": 1,
      "tags": ["balance", "comfort", "europe"],
      "details": {
        "departure_date": "2025-08-08",
        "return_date": "2025-08-15",
        "flight": {
          "route": "MOW -> PRG",
          "type": "1 stop",
          "baggage": "carry-on only"
        },
        "hotel": {
          "name": "Hotel Royal Prague",
          "stars": 4,
          "location": "city center",
          "nights": 7
        }
      },
      "cta": {
        "label": "Book now",
        "url": "https://affiliate.example.com/booking?package=opt-001"
      }
    }
  ]
}
```

### 3. GET `/api/v1/packages/popular`

Description: return prepared package concepts and popular directions for the frontend.

Response JSON:

```json
{
  "packages": [
    {
      "package_id": "wild-101",
      "title": "Wildcard: Romanian castles",
      "description": "A surprising destination with strong logistics and a budget-friendly route.",
      "direction": "Romania",
      "tags": ["wildcard", "culture", "roadtrip"]
    }
  ]
}
```

### 4. GET `/api/v1/health`

Description: service health check.

Response JSON:

```json
{
  "status": "ok",
  "version": "0.1.0",
  "uptime_seconds": 86400
}
```

### 5. POST `/api/v1/feedback` (optional)

Description: collect user feedback on search results to improve package quality.

Request JSON:

```json
{
  "request_id": "abc123",
  "package_id": "opt-001",
  "rating": 4,
  "comment": "I liked the option, but I would like to see more beach trips",
  "improvement_suggestions": ["more beach destinations"]
}
```

Response JSON:

```json
{
  "success": true,
  "message": "Thank you! Your feedback has been received."
}
```

---

## "Find at Any Cost" algorithm

### Rules
- Budget is the primary filter.
- Dates and trip length are flexible.
- Preferences matter, but budget has priority.
- If no perfect package exists, the system applies fallback levels instead of returning empty results.

### Fallback levels

1. Transport
   - Replace a direct flight with a flight that has a stop.
   - Replace a plane with a night train or bus.
   - Remove checked baggage and keep only carry-on.
   - Use cheaper departure or return dates.

2. Accommodation
   - Downgrade from a 4-star hotel to private apartments or a hostel room.
   - Move outside the city center while keeping reasonable access.
   - Preserve the overall comfort profile while lowering cost.

3. Duration
   - Shorten the trip length.
   - Offer "7 days instead of 10" if budget is tight.
   - Shift dates within the requested window.

4. Destination
   - Find a cheaper destination with a similar mood.
   - Replace Spain with Albania, or Paris with Budapest.
   - Keep the same travel vibe: sea, city, culture.

5. Micro-tourism / Extreme fallback
   - For a tiny budget, propose a nearby city trip by train or bus.
   - Use a hostel, glamping, or an unusual overnight stay.
   - Deliver a travel experience even if it isn't international.

### Implementation approach
- `search_service.py` performs the initial budget-based search.
- If no package is found, `fallback_engine.py` is invoked.
- The fallback engine tries levels sequentially and returns alternative packages.
- Each level may return 1-2 valid packages when available.
- The frontend receives prepared scenarios tagged by `fallback_level`.
- For MVP, return 3-4 concepts: optimal, comfort, adventure, wildcard.

---

## Data sources and MVP strategy

### Data sources
- Flights: Kiwi.com Tequila API, Skyscanner or Amadeus for classic searches.
- Accommodation: Booking.com Affiliate API and hostel/apartment aggregators.
- Ground transport: Omio API, Flixbus, and train/bus providers.

### MVP strategy
- Do not attempt full global "anywhere" search immediately.
- Use a curated list of 50-100 popular destinations.
- Cache prices once per day.
- Serve requests from local cache or precomputed repository to reduce API costs.
- Return ready-made package concepts instead of full real-time itinerary assembly.

---

## Development plan

1. Create the FastAPI skeleton and project structure.
2. Implement request and response models with Pydantic.
3. Build a stub search engine and seed popular destination data.
4. Add fallback logic and several preset package concepts.
5. Add a caching layer.
6. Implement `/search`, `/search/{request_id}`, `/packages/popular`, and `/health` endpoints.
7. Write tests for main search and fallback scenarios.
8. Document the API and provide example frontend payloads.

---

## Platform and MVP region recommendation

- Platform: React + FastAPI is a strong combination for a web MVP.
- MVP region: start with CIS/Europe. This makes it easier to combine buses, trains, and budget air routes.
- Later expansion: add the US market with domestic low-cost flights and local hotels.

---

## Example final package JSON

```json
{
  "package_id": "adventure-003",
  "title": "Adventure: Budapest and surroundings",
  "description": "A farther flight plus budget lodging and a cool city route.",
  "direction": "Budapest, Hungary",
  "days": 7,
  "total_price": 970,
  "currency": "USD",
  "budget_breakdown": {
    "transport": 450,
    "accommodation": 260,
    "activities": 130,
    "local_transport": 80,
    "buffer": 50
  },
  "fallback_level": 2,
  "tags": ["adventure", "budget", "city"],
  "transport_summary": "One-stop flight, carry-on only, airport bus transfer.",
  "accommodation_summary": "Hostel or apartment outside center with good reviews.",
  "details": {
    "departure_date": "2025-08-12",
    "return_date": "2025-08-19",
    "flight": {
      "route": "MOW -> BUD",
      "type": "1 stop",
      "baggage": "carry-on only"
    },
    "hotel": {
      "name": "Central Hostel",
      "type": "hostel",
      "location": "Budapest, Pest",
      "nights": 7
    }
  },
  "cta": {
    "label": "View details",
    "url": "https://affiliate.example.com/package/adventure-003"
  }
}
```
- If no suitable package is found, fallback levels are applied automatically.

### Fallback levels

1. Transport
   - Replace a direct flight with a connecting flight.
   - Replace the plane with a night train or bus.
   - Remove checked baggage and keep carry-on only.
   - Choose earlier or later flights for lower prices.

2. Accommodation
   - Downgrade from a 4-star hotel to a private apartment, guesthouse, or hostel.
   - Move outside the center while keeping reasonable access.
   - Preserve comfort preferences while lowering cost.

3. Duration
   - Shorten the trip length.
   - Offer "7 days instead of 10." 
   - Shift dates within the requested range.

4. Destination
   - Find a cheaper destination with a similar profile.
   - Replace Turkey with Albania, Paris with Budapest, etc.
   - Keep the same trip mood: sea, culture, city.

5. Micro-tourism / Extreme fallback
   - If the budget is very low, suggest a trip to a nearby city or region.
   - Use train, bus, and an overnight stay in a hostel or glamping.
   - Deliver a travel experience even if it isn't an international trip.

### How to implement
- `search_service.py` runs the initial budget-based search.
- If no package is found, it calls `fallback_engine.py`.
- `fallback_engine` tries levels sequentially and builds alternatives.
- Each level returns 1-2 packages if available.
- The frontend receives ready-made scenarios tagged with `fallback_level`.
- For MVP, prefer returning 3-4 concepts: optimal, comfort, adventure, wildcard.

---

## Data sources and MVP strategy

### Data sources
- Flights: Kiwi.com Tequila API, Skyscanner or Amadeus for baseline results.
- Accommodation: Booking.com Affiliate API, plus hostel/apartment aggregators.
- Ground transport: Omio API, Flixbus, and train/bus providers.

### MVP strategy
- Do not attempt full global "anywhere" search immediately.
- Use a curated list of 50-100 popular destinations.
- Cache prices once per day.
- Serve requests from local cache or a precomputed repository instead of frequent API calls.
- Return ready-made package concepts instead of full real-time itinerary assembly.

---

## Development plan

1. Create the FastAPI skeleton and project structure.
2. Implement request and response models with Pydantic.
3. Build a stub search engine and seed popular destination data.
4. Add fallback logic and several preset package concepts.
5. Add a caching layer.
6. Implement `/search`, `/search/{request_id}`, `/packages/popular`, and `/health` endpoints.
7. Write tests for main search and fallback scenarios.
8. Document the API and provide example frontend payloads.

---

## Platform and MVP region recommendation

- Platform: React + FastAPI is a strong combination for a web MVP.
- MVP region: start with CIS/Europe. This makes it easier to combine buses, trains, and budget air routes.
- Later expansion: add the US market with domestic low-cost flights and local hotels.

---

## Example final package JSON

```json
{
  "package_id": "adventure-003",
  "title": "Adventure: Budapest and surroundings",
  "description": "A farther flight plus budget lodging and a cool city route.",
  "direction": "Budapest, Hungary",
  "days": 7,
  "total_price": 970,
  "currency": "USD",
  "budget_breakdown": {
    "transport": 450,
    "accommodation": 260,
    "activities": 130,
    "local_transport": 80,
    "buffer": 50
  },
  "fallback_level": 2,
  "tags": ["adventure", "budget", "city"],
  "transport_summary": "One-stop flight, carry-on only, airport bus transfer.",
  "accommodation_summary": "Hostel or apartment outside center with good reviews.",
  "details": {
    "departure_date": "2025-08-12",
    "return_date": "2025-08-19",
    "flight": {
      "route": "MOW -> BUD",
      "type": "1 stop",
      "baggage": "carry-on only"
    },
    "hotel": {
      "name": "Central Hostel",
      "type": "hostel",
      "location": "Budapest, Pest",
      "nights": 7
    }
  },
  "cta": {
    "label": "View details",
    "url": "https://affiliate.example.com/package/adventure-003"
  }
}
```
