# Error responses are raised (HTTPException), not returned — see the
# handlers at the bottom of this file, wired up in app/main.py, which turn
# any HTTPException (ours or FastAPI's own) into the shared envelope:
#   {"errors": [{"code", "title", "detail", "status", "instance", "meta"?}]}
import logging
from http import HTTPStatus
from typing import Any, Dict, Optional, Union

from fastapi import status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.requests import Request


def json_response(
    status_code: int, data: Dict[str, Any], response_headers: Dict[str, str] = None
) -> JSONResponse:
    return JSONResponse(content=data, status_code=status_code, headers=response_headers)


def success_response(
    data: Dict[str, Any],
    status_code: int = status.HTTP_200_OK,
    response_headers: Dict[str, str] = None,
):
    return JSONResponse(content=data, status_code=status_code, headers=response_headers)


def _raise(
    status_code: int,
    detail: Union[str, Dict[str, Any]],
    headers: Optional[Dict[str, str]] = None,
    code: Optional[str] = None,
):
    """
    detail can be a plain message, or a dict with "message" plus any extra
    fields the caller wants surfaced (e.g. validate.py's `valid: False`) —
    those extras land in the error object's "meta". `code` is optional; the
    handler falls back to the HTTP status name (e.g. "NOT_FOUND").
    """
    if code:
        if isinstance(detail, dict):
            detail = {**detail, "code": code}
        else:
            detail = {"message": detail, "code": code}
    raise HTTPException(status_code=status_code, detail=detail, headers=headers)


def bad_request(
    detail: Union[str, Dict[str, Any]],
    headers: Optional[Dict[str, str]] = None,
    code: Optional[str] = None,
):
    _raise(status.HTTP_400_BAD_REQUEST, detail, headers, code)


def unauthorized(
    detail: Union[str, Dict[str, Any]],
    headers: Optional[Dict[str, str]] = None,
    code: Optional[str] = None,
):
    _raise(status.HTTP_401_UNAUTHORIZED, detail, headers, code)


def forbidden(
    detail: Union[str, Dict[str, Any]],
    headers: Optional[Dict[str, str]] = None,
    code: Optional[str] = None,
):
    _raise(status.HTTP_403_FORBIDDEN, detail, headers, code)


def not_found(
    detail: Union[str, Dict[str, Any]],
    headers: Optional[Dict[str, str]] = None,
    code: Optional[str] = None,
):
    _raise(status.HTTP_404_NOT_FOUND, detail, headers, code)


def invalid_file_type(
    detail: Union[str, Dict[str, Any]],
    headers: Optional[Dict[str, str]] = None,
    code: Optional[str] = None,
):
    _raise(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail, headers, code)


def unprocessable_entity(
    detail: Union[str, Dict[str, Any]],
    headers: Optional[Dict[str, str]] = None,
    code: Optional[str] = None,
):
    _raise(status.HTTP_422_UNPROCESSABLE_ENTITY, detail, headers, code)


def internal_server_error(
    detail: Union[str, Dict[str, Any]],
    headers: Optional[Dict[str, str]] = None,
    code: Optional[str] = None,
):
    _raise(status.HTTP_500_INTERNAL_SERVER_ERROR, detail, headers, code)


def error_uploading_file(
    detail: Union[str, Dict[str, Any]],
    headers: Optional[Dict[str, str]] = None,
    code: Optional[str] = None,
):
    _raise(status.HTTP_500_INTERNAL_SERVER_ERROR, detail, headers, code)


def _error_object(request: Request, status_code: int, detail, code: Optional[str] = None) -> Dict[str, Any]:
    meta = None
    if isinstance(detail, dict):
        message = detail.get("message", "")
        code = detail.get("code", code)
        meta = {k: v for k, v in detail.items() if k not in ("message", "code")}
    else:
        message = detail

    error = {
        "code": code or HTTPStatus(status_code).name,
        "title": HTTPStatus(status_code).phrase,
        "detail": message,
        "status": status_code,
        "instance": request.url.path,
    }
    if meta:
        error["meta"] = meta
    return error


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    error = _error_object(request, exc.status_code, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder({"errors": [error]}),
        headers=exc.headers,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = [
        {
            "code": "VALIDATION_ERROR",
            "title": HTTPStatus.UNPROCESSABLE_ENTITY.phrase,
            "detail": f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}",
            "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "instance": request.url.path,
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"errors": errors}),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logging.exception("Unhandled exception on %s", request.url.path)
    error = _error_object(
        request,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "An unexpected error occurred.",
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder({"errors": [error]}),
    )
