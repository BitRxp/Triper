from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.domain import FallbackLevel, SearchStatus, TravelType
from app.models.requests import SearchRequest


class DestinationSchema(BaseModel):
    id: str
    name: str
    country: str
    region: str
    description: str
    tags: List[str]
    travel_profile: List[str]
    example_price_usd: Optional[float] = None
    popular: bool = True


class BudgetBreakdownSchema(BaseModel):
    transport: float
    accommodation: float
    activities: float
    local_transport: Optional[float] = 0.0
    buffer: Optional[float] = 0.0


class FlightInfoSchema(BaseModel):
    route: str
    type: str
    baggage: str


class HotelInfoSchema(BaseModel):
    name: str
    type: str
    location: str
    stars: Optional[int] = None
    nights: int


class PackageDetailsSchema(BaseModel):
    departure_date: datetime
    return_date: datetime
    flight: FlightInfoSchema
    hotel: HotelInfoSchema


class CTASchema(BaseModel):
    label: str
    url: str


class PackageSchema(BaseModel):
    package_id: str
    title: str
    description: str
    direction: str
    days: int
    total_price: float
    currency: str
    budget_breakdown: BudgetBreakdownSchema
    fallback_level: FallbackLevel
    tags: List[str]
    travel_type: TravelType
    transport_summary: str
    accommodation_summary: str
    details: PackageDetailsSchema
    cta: CTASchema


class SearchResultSchema(BaseModel):
    request_id: str
    status: SearchStatus
    request: SearchRequest
    packages: List[PackageSchema] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
