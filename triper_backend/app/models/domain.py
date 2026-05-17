from enum import Enum, IntEnum


class DateType(str, Enum):
    exact = "exact"
    window = "window"
    seasonal = "seasonal"
    flexible = "flexible"


class SearchStatus(str, Enum):
    processing = "processing"
    completed = "completed"
    error = "error"


class TravelType(str, Enum):
    flight_hotel = "flight+hotel"
    train_hotel = "train+hotel"
    bus_hotel = "bus+hotel"


class FallbackLevel(IntEnum):
    none = 0
    transport = 1
    accommodation = 2
    duration = 3
    destination = 4
    micro_tourism = 5
