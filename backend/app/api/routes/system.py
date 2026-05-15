from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.system import SystemStatus
from app.services.system_status_service import build_system_status

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/status", response_model=SystemStatus)
def get_system_status(session: Session = Depends(get_session)) -> dict:
    return build_system_status(session)
