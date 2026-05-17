from datetime import date, datetime, timedelta
from typing import List, Optional
from uuid import uuid4

from app.db.repository import InMemoryRepository
from app.db.schemas import PackageSchema, SearchResultSchema
from app.models.domain import FallbackLevel, SearchStatus, TravelType
from app.models.requests import SearchRequest
from app.services.external_adapters import SkyscannerAdapter


class SearchService:
    def __init__(self, repository: Optional[InMemoryRepository] = None):
        self.repository = repository or InMemoryRepository()

    def search(self, request: SearchRequest) -> SearchResultSchema:
        request_id = str(uuid4())
        packages = self._find_packages(request)
        result = SearchResultSchema(
            request_id=request_id,
            status=SearchStatus.processing,
            request=request,
            packages=packages,
        )
        self.repository.save_search_result(result)
        return result

    def load_search_result(self, request_id: str) -> Optional[SearchResultSchema]:
        result = self.repository.load_search_result(request_id)
        if result and result.status == SearchStatus.processing:
            result.status = SearchStatus.completed
            result.updated_at = datetime.utcnow()
            self.repository.save_search_result(result)
        return result

    def _find_packages(self, request: SearchRequest) -> List[PackageSchema]:
        adapter = SkyscannerAdapter()
        if adapter.enabled:
            origin_data = adapter.search_airport(request.origin)
            if origin_data:
                origin_sky_id = origin_data.get("skyId") or origin_data.get("id")
                origin_entity_id = origin_data.get("entityId") or origin_data.get("id")
                if origin_sky_id and origin_entity_id:
                    departure_date = self._choose_departure_date(request)
                    duration_days = self._choose_duration(request)
                    return_date = departure_date + timedelta(days=duration_days)
                    flight_results = adapter.search_flight_everywhere(
                        origin_sky_id=origin_sky_id,
                        origin_entity_id=origin_entity_id,
                        departure_date=departure_date,
                        return_date=return_date,
                        adults=request.travelers,
                        cabin_class="economy",
                        currency=request.currency,
                        market="US",
                    )
                    if flight_results:
                        offers = adapter.build_flight_offers(
                            request.origin,
                            flight_results,
                            departure_date,
                            duration_days,
                            request.currency,
                        )
                        packages = [
                            self._create_package_from_offer(offer, request, duration_days)
                            for offer in offers
                        ]
                        packages = [p for p in packages if p is not None]
                        if packages:
                            return packages[:4]

        return self._seed_packages(request)

    def _choose_departure_date(self, request: SearchRequest) -> date:
        if request.date_range:
            return request.date_range.from_date
        return date.today() + timedelta(days=14)

    def _choose_duration(self, request: SearchRequest) -> int:
        if request.duration:
            return request.duration.min_days
        return 7

    def _create_package_from_offer(
        self,
        offer: dict,
        request: SearchRequest,
        duration_days: int,
    ) -> Optional[PackageSchema]:
        try:
            departure_date = self._parse_date(offer.get("departure_date"))
            return_date = self._parse_date(offer.get("return_date"))
            if not return_date:
                return_date = departure_date + timedelta(days=duration_days)

            days = (return_date - departure_date).days
            if days <= 0:
                days = max(duration_days, 1)
                return_date = departure_date + timedelta(days=days)

            total_price = float(offer.get("total_price") or request.budget) * request.travelers
            destination = offer.get("destination") or "Unknown destination"
            description = f"Live flight offer to {destination} with budget-aware pricing."

            transport = round(total_price * 0.55, 2)
            accommodation = round(total_price * 0.3, 2)
            activities = round(total_price * 0.1, 2)
            buffer_value = round(total_price - transport - accommodation - activities, 2)
            if buffer_value < 0:
                buffer_value = 0.0

            return PackageSchema(
                package_id=f"skyscanner-{destination.lower().replace(' ', '-')}-{int(total_price)}",
                title=f"Live deal: {destination} for {days} days",
                description=description,
                direction=destination,
                days=days,
                total_price=total_price,
                currency=request.currency,
                budget_breakdown={
                    "transport": transport,
                    "accommodation": accommodation,
                    "activities": activities,
                    "local_transport": 0.0,
                    "buffer": buffer_value,
                },
                fallback_level=FallbackLevel.none,
                tags=["flight", "live"] + (request.preferences or []),
                travel_type=TravelType.flight_hotel,
                transport_summary=offer.get("transport_summary") or "Flight offer from Skyscanner",
                accommodation_summary=f"Hotel matched to {destination} based on budget.",
                details={
                    "departure_date": departure_date,
                    "return_date": return_date,
                    "flight": {
                        "route": f"{request.origin} -> {destination}",
                        "type": "economy",
                        "baggage": "standard",
                    },
                    "hotel": {
                        "name": f"{destination} Comfort Hotel",
                        "type": "hotel",
                        "location": "city center",
                        "stars": 4,
                        "nights": days,
                    },
                },
                cta={
                    "label": "Book now",
                    "url": offer.get("booking_url"),
                },
            )
        except Exception:
            return None

    def _parse_date(self, value: Optional[str]) -> Optional[date]:
        if not value:
            return None
        try:
            if "T" in value:
                return datetime.fromisoformat(value).date()
            return datetime.fromisoformat(value).date()
        except ValueError:
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except Exception:
                return None

    def _seed_packages(self, request: SearchRequest) -> List[PackageSchema]:
        candidates = self.repository.get_seed_packages()
        exact_matches = [p for p in candidates if p.total_price <= request.budget]

        if exact_matches:
            sorted_matches = sorted(exact_matches, key=lambda p: (p.fallback_level, p.total_price))
            return sorted_matches[:4]

        fallback_packages = sorted(candidates, key=lambda p: (p.total_price, p.fallback_level))
        return fallback_packages[:4]
