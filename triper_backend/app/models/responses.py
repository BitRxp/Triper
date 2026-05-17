from datetime import date
from typing import List, Optional

from pydantic import BaseModel

from app.models.domain import FallbackLevel, SearchStatus, TravelType


class BudgetBreakdown(BaseModel):
    transport: float
    accommodation: float
    activities: float
    local_transport: Optional[float] = 0.0
    buffer: Optional[float] = 0.0


class FlightInfo(BaseModel):
    route: str
    type: str
    baggage: str


class HotelInfo(BaseModel):
    name: str
    type: str
    location: str
    stars: Optional[int] = None
    nights: int


class PackageDetails(BaseModel):
    departure_date: date
    return_date: date
    flight: FlightInfo
    hotel: HotelInfo


class CTA(BaseModel):
    label: str
    url: str


class PackageResponse(BaseModel):
    package_id: str
    title: str
    description: str
    direction: str
    days: int
    total_price: float
    currency: str
    budget_breakdown: BudgetBreakdown
    fallback_level: FallbackLevel
    tags: List[str]
    travel_type: Optional[TravelType] = None
    transport_summary: str
    accommodation_summary: str
    details: PackageDetails
    cta: CTA


class SearchResponse(BaseModel):
    request_id: str
    status: SearchStatus
    eta_seconds: Optional[int] = None
    duration_seconds: Optional[int] = None
    summary: Optional[str] = None
    packages: List[PackageResponse] = []


class PackageSummary(BaseModel):
    package_id: str
    title: str
    description: str
    direction: str
    tags: List[str]


class PopularPackagesResponse(BaseModel):
    packages: List[PackageSummary]
