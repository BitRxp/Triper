from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, PositiveInt, constr, confloat, model_validator

from app.models.domain import DateType


class DateRange(BaseModel):
    from_date: date = Field(..., alias="from")
    to_date: date = Field(..., alias="to")

    @model_validator(mode="after")
    def validate_dates(self):
        today = date.today()
        if self.from_date < today or self.to_date < today:
            raise ValueError("Travel dates cannot be in the past")
        if self.to_date < self.from_date:
            raise ValueError("The 'to' date must be the same as or after the 'from' date")
        return self

    class Config:
        validate_by_name = True


class Duration(BaseModel):
    min_days: PositiveInt
    max_days: PositiveInt


class SearchRequest(BaseModel):
    origin: str
    travelers: PositiveInt = 1
    budget: confloat(gt=0)
    currency: constr(min_length=3, max_length=3)
    date_type: DateType
    date_range: Optional[DateRange] = None
    duration: Optional[Duration] = None
    preferences: Optional[List[str]] = None
    mood: Optional[str] = None

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "origin": "Helsinki",
                "travelers": 2,
                "budget": 1000,
                "currency": "USD",
                "date_type": "flexible",
                "date_range": {"from": "2025-08-01", "to": "2025-08-31"},
                "duration": {"min_days": 7, "max_days": 10},
                "preferences": ["sea", "architecture"],
                "mood": "surprise",
            }
        }


class FeedbackRequest(BaseModel):
    request_id: str
    package_id: str
    rating: PositiveInt
    comment: Optional[str] = None
    improvement_suggestions: Optional[List[str]] = None
