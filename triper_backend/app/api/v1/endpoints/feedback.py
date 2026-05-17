from fastapi import APIRouter

from app.db.repository import get_repository
from app.db.schemas import FeedbackSchema
from app.models.requests import FeedbackRequest
from app.models.responses import FeedbackResponse

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(request: FeedbackRequest):
    repository = get_repository()
    feedback = FeedbackSchema(
        request_id=request.request_id,
        package_id=request.package_id,
        rating=request.rating,
        comment=request.comment,
        improvement_suggestions=request.improvement_suggestions,
    )
    repository.save_feedback(feedback)
    return FeedbackResponse(
        success=True,
        message="Thank you for your feedback! We will use it to improve our recommendations.",
    )
