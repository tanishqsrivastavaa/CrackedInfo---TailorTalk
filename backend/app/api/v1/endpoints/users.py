from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.db.session import get_session
from app.crud.user import create_user
from app.models.user import User

router = APIRouter()

@router.post("/")
def create_user_route(user: User, session: Session = Depends(get_session)):
    return create_user(session, user)
