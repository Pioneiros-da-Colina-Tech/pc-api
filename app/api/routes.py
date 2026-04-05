from fastapi import APIRouter, status

from app.attendance.routes import router as attendance_router
from app.auth.routes import router as auth_router
from app.classes.routes import router as classes_router
from app.club_year.routes import router as club_year_router
from app.meetings.routes import router as meetings_router
from app.roles.routes import router as roles_router
from app.specialties.routes import router as specialties_router
from app.units.routes import router as units_router

from .schemas import BaseResponseSchema

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check() -> BaseResponseSchema[None]:
    """Health check endpoint."""
    return BaseResponseSchema[None](message="healthy", data=None)


router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(meetings_router, prefix="/meetings", tags=["Meetings"])
router.include_router(
    attendance_router, prefix="/meetings", tags=["Attendance"]
)
router.include_router(roles_router, prefix="/roles", tags=["Roles"])
router.include_router(
    club_year_router, prefix="/club-years", tags=["Club Years"]
)
router.include_router(classes_router, prefix="/classes", tags=["Classes"])
router.include_router(units_router, prefix="/units", tags=["Units"])
router.include_router(
    specialties_router, prefix="/specialties", tags=["Specialties"]
)
