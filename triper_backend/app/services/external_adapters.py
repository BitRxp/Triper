from datetime import date
from typing import Any, Dict, List, Optional

import httpx

from app.core.settings import settings


class SkyscannerAdapter:
    BASE_URL = "https://skyscanner-flights-travel-api.p.rapidapi.com"

    def __init__(self, client: Optional[httpx.Client] = None):
        self.host = settings.rapidapi_skyscanner_host
        self.api_key = settings.rapidapi_skyscanner_key
        self.timeout = settings.rapidapi_timeout_seconds
        self.client = client or httpx.Client(timeout=self.timeout)
        self.headers = {
            "x-rapidapi-key": self.api_key or "",
            "x-rapidapi-host": self.host or "skyscanner-flights-travel-api.p.rapidapi.com",
        }

    @property
    def enabled(self) -> bool:
        return bool(self.api_key and self.host)

    def _request(self, path: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.enabled:
            return None

        url = f"{self.BASE_URL}{path}"
        try:
            response = self.client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    def search_airport(self, query: str) -> Optional[Dict[str, Any]]:
        payload = self._request("/flights/searchAirport", {"query": query})
        if not payload:
            return None

        if isinstance(payload, dict):
            places = payload.get("places") or payload.get("data") or payload.get("results")
            if isinstance(places, list) and places:
                return places[0]
        if isinstance(payload, list) and payload:
            return payload[0]
        return None

    def search_flight_everywhere(
        self,
        origin_sky_id: str,
        origin_entity_id: str,
        departure_date: date,
        adults: int = 1,
        cabin_class: str = "economy",
        currency: str = "USD",
        market: str = "US",
    ) -> List[Dict[str, Any]]:
        params = {
            "originSkyId": origin_sky_id,
            "originEntityId": origin_entity_id,
            "date": departure_date.isoformat(),
            "adults": str(adults),
            "cabinClass": cabin_class,
            "currency": currency,
            "market": market,
        }
        payload = self._request("/flights/searchFlightEverywhere", params)
        if not payload:
            return []

        results = payload.get("destinations") or payload.get("data") or payload.get("results") or payload.get("quotes") or []
        if isinstance(results, dict):
            results = results.get("data") or results.get("results") or []

        if isinstance(results, list):
            return results[:8]
        return []

    def build_flight_offers(
        self,
        origin: str,
        destination_results: List[Dict[str, Any]],
        departure_date: date,
        duration_days: int,
        currency: str,
    ) -> List[Dict[str, Any]]:
        offers = []
        for index, item in enumerate(destination_results):
            destination = (
                item.get("destinationName")
                or item.get("destinationCity")
                or item.get("name")
                or item.get("destination")
                or item.get("city")
                or "Unknown destination"
            )
            price = item.get("price") or item.get("minPrice") or item.get("bestPrice")
            if price is None:
                continue

            try:
                total_price = float(price)
            except (TypeError, ValueError):
                continue

            departure_iso = item.get("departureDate") or departure_date.isoformat()
            return_iso = item.get("returnDate")
            offers.append(
                {
                    "destination": destination,
                    "total_price": total_price,
                    "currency": currency,
                    "departure_date": departure_iso,
                    "return_date": return_iso,
                    "origin": origin,
                    "booking_url": item.get("deeplinkUrl") or item.get("bookingUrl") or "https://rapidapi.com/elis-lab-elis-lab-default/api/skyscanner-flights-travel-api",
                    "transport_summary": item.get("transportSummary") or item.get("route") or "Flight search result",
                    "stops": item.get("stops") or item.get("stopCount") or "direct",
                    "tags": item.get("tags") or ["flight", "budget"],
                }
            )
        return offers
