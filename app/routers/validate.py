from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from app.schemas import validate as schema
from app.models import User
from app.database import get_db
from app.utils.http import forbidden, success_response

router = APIRouter(prefix="/validate", tags=["Validation"])


@router.post(
    "/email",
    responses={
        200: {
            "description": "User can continue with registration.",
            "content": {"application/json": {"example": {"valid": True}}},
        },
        403: {
            "description": "User already has a registration with login access.",
            "content": {
                "application/json": {
                    "example": {
                        "valid": False,
                        "message": "You already have an account. Please login!",
                    }
                }
            },
        },
    },
)
def validate_email_input(
    request_body: schema.EmailInput, db: Session = Depends(get_db)
):
    db_users = (
        db.query(User)
        .filter(
            User.email == request_body.email,
            User.login_allowed == 1,
            User.is_deleted == 0,
        )
        .all()
    )
    if len(db_users) > 0:
        return forbidden(
            {"valid": False, "message": "You already have an account. Please login!"}
        )
    else:
        return success_response({"valid": True})
