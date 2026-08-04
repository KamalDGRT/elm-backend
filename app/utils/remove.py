from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.endpoints import EndpointRole


def remove_role_for_endpoint(db: Session, endpoint_id: int, role_id: int):
    """
    Call this function only when you are very sure that both:
    The endpoint_id and role_id exist in endpoint_role table.
    """
    endpoint_query = db.query(EndpointRole).filter(
        EndpointRole.endpoint_id == endpoint_id, EndpointRole.role_id == role_id
    )
    endpoint_query.delete(synchronize_session=False)
    db.commit()


def delete_response(response_content: dict = {"message": "Deleted successfully!"}):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(response_content)
    )
