from fastapi import APIRouter, status

from app.infra.database.adapter import SessionContext

from .domain import CreateMeetingUseCase
from .schemas import CreateMeetingSchema

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_meeting(payload: CreateMeetingSchema, session: SessionContext):
    return await CreateMeetingUseCase(payload, session).execute()


# @router.get("")
# async def get_meetings():
#     return BaseResponseSchema(message="Meetings", data=None)
