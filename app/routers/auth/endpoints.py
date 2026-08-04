from typing import List

from fastapi import status, Depends, APIRouter
from sqlalchemy.orm import Session

from app.db.endpoints import EndpointRole
from app.models import Endpoint
from app.oauth2 import get_current_user
from app.database import get_db
from app.schemas.auth import endpoint as schema
from app.schemas.auth.user import UserOut
from app.utils.auth import check_permissions
from app.utils.create import add_role_for_endpoint, create_endpoint
from app.utils.fetch import get_roles_for_endpoint
from app.utils.remove import delete_response, remove_role_for_endpoint
from app.utils.time import get_current_time
from app.utils.http import not_found

router = APIRouter(prefix="/endpoint", tags=["Endpoints"])


@router.get("/all", response_model=List[schema.Endpoint], include_in_schema=False)
def get_all_endpoints(
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    results_data = db.query(Endpoint).all()

    results = list()
    for endpoint in results_data:
        results.append(schema.Endpoint(
            endpoint_id=endpoint.endpoint_id,
            endpoint_name=endpoint.endpoint_name,
            is_common=endpoint.is_common,
            is_disabled=endpoint.is_disabled,
            method=endpoint.method,
            category=endpoint.category,
            roles=get_roles_for_endpoint(db, endpoint.endpoint_id),
            created_at=endpoint.created_at,
            updated_at=endpoint.updated_at,
            creator=endpoint.creator,
            updater=endpoint.updater
        ))
    return results


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=schema.EndpointOut,
    include_in_schema=False,
)
def create_an_endpoint(
    request_body: schema.EndpointCreate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    return create_endpoint(db, request_body, current_user.user_id)


@router.post(
    "/create-many",
    status_code=status.HTTP_201_CREATED,
    response_model=List[schema.EndpointOut],
    include_in_schema=False,
)
def create_many_roles(
    request_body: List[schema.EndpointCreate],
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    new_endpoints = list()
    for endpoint_data in request_body:
        new_endpoint = create_endpoint(db, endpoint_data, current_user.user_id)
        new_endpoints.append(new_endpoint)

    return new_endpoints


@router.post("/info", response_model=schema.Endpoint, include_in_schema=False)
def get_endpoint_info(
    request_body: schema.EndpointName,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    endpoint = (
        db.query(Endpoint)
        .filter(Endpoint.endpoint_name == request_body.endpoint_name)
        .first()
    )

    if not endpoint:
        not_found(f"Endpoint with name: { request_body.endpoint_name } not found!")

    return schema.Endpoint(
        endpoint_id=endpoint.endpoint_id,
        endpoint_name=endpoint.endpoint_name,
        is_common=endpoint.is_common,
        is_disabled=endpoint.is_disabled,
        roles=get_roles_for_endpoint(db, endpoint.endpoint_id),
        created_at=endpoint.created_at,
        updated_at=endpoint.updated_at,
        creator=endpoint.creator,
        updater=endpoint.updater,
    )


@router.delete(
    "/delete", status_code=status.HTTP_200_OK, include_in_schema=False
)
def delete_an_endpoint_detail(
    request_body: schema.EndpointName,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    endpoint_query = db.query(Endpoint).filter(
        Endpoint.endpoint_name == request_body.endpoint_name
    )
    endpoint = endpoint_query.first()

    if endpoint is None:
        not_found(f"Endpoint with name: { request_body.endpoint_name } does not exist!")

    endpoint_query.delete(synchronize_session=False)
    db.commit()

    return delete_response()


@router.put(
    "/update",
    response_model=schema.EndpointOut,
    include_in_schema=False,
)
def update_role(
    request_body: schema.EndpointUpdateRequest,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):

    endpoint_query = db.query(Endpoint).filter(
        Endpoint.endpoint_id == request_body.endpoint_id
    )
    endpoint = endpoint_query.first()

    if endpoint is None:
        not_found(f"Endpoint with id: { request_body.endpoint_id } does not exist!")

    input_data = request_body.model_dump()
    input_data.pop("roles")
    input_data["updated_at"] = get_current_time()
    input_data["updated_by"] = current_user.user_id
    endpoint_query.update(input_data, synchronize_session=False)
    db.commit()

    endpoint_roles_data = (
        db.query(EndpointRole)
        .filter(EndpointRole.endpoint_id == request_body.endpoint_id)
        .all()
    )
    endpoint_roles = set([role.role_id for role in endpoint_roles_data])
    input_roles = set([role.role_id for role in request_body.roles])

    if input_roles != endpoint_roles:
        new_input_roles = input_roles.difference(endpoint_roles)
        for role in new_input_roles:
            add_role_for_endpoint(db, request_body.endpoint_id, role)

        db_roles = endpoint_roles.difference(input_roles)
        for role in db_roles:
            remove_role_for_endpoint(db, request_body.endpoint_id, role)

    updated_endpoint = endpoint_query.first()
    return schema.EndpointOut(
        endpoint_id=updated_endpoint.endpoint_id,
        is_common=updated_endpoint.is_common,
        is_disabled=updated_endpoint.is_disabled,
        method=updated_endpoint.method,
        category=updated_endpoint.category,
        endpoint_name=updated_endpoint.endpoint_name,
        roles=get_roles_for_endpoint(db, updated_endpoint.endpoint_id),
        created_at=updated_endpoint.created_at,
    )
