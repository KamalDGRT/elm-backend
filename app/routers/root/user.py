from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import UpdatePasswordLog, User
from app.oauth2 import require_root
from app.schemas.auth import user as schema
from app.utils.auth import hash
from app.utils.time import get_current_time
from app.utils.http import not_found, success_response

router = APIRouter(prefix="/root/user", tags=["Root"], dependencies=[Depends(require_root)])


@router.post("/update-password", include_in_schema=False)
def update_user_password(
    request_body: schema.UpdateUserPassword,
    db: Session = Depends(get_db),
    current_user: schema.UserOut = Depends(require_root),
):
    """
    Resets any user's password without knowing the current one.
    """
    user = db.query(User).filter(User.user_id == request_body.user_id).first()
    if not user:
        return not_found(f"User with id: { request_body.user_id } does not exist!")

    user.password = hash(request_body.new_password)
    user.updated_at = get_current_time()
    db.add(
        UpdatePasswordLog(
            user_id=user.user_id,
            updated_by=current_user.user_id,
            updated_at=get_current_time(),
        )
    )
    db.commit()

    return success_response({"message": "Password updated successfully."})
