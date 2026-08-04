# This file is solely to have the HTTP Status Code Exceptions.
from typing import Dict, Any
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse


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


def bad_request(
    data: Dict[str, Any], response_headers: Dict[str, str] = None
) -> JSONResponse:
    return JSONResponse(
        content=data, status_code=status.HTTP_400_BAD_REQUEST, headers=response_headers
    )


def unauthorized(data: Dict[str, Any], response_headers: Dict[str, str] = None):
    return JSONResponse(
        content=data, status_code=status.HTTP_401_UNAUTHORIZED, headers=response_headers
    )


def forbidden(
    data: Dict[str, Any], response_headers: Dict[str, str] = None
) -> JSONResponse:
    return JSONResponse(
        content=data, status_code=status.HTTP_403_FORBIDDEN, headers=response_headers
    )


def not_found(
    data: Dict[str, Any], response_headers: Dict[str, str] = None
) -> JSONResponse:
    return JSONResponse(
        content=data, status_code=status.HTTP_404_NOT_FOUND, headers=response_headers
    )


def invalid_file_type(
    data: Dict[str, Any], response_headers: Dict[str, str] = None
) -> JSONResponse:
    return JSONResponse(
        content=data,
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        headers=response_headers,
    )


def unprocessable_entity(
    data: Dict[str, Any], response_headers: Dict[str, str] = None
) -> JSONResponse:
    return JSONResponse(
        content=data,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        headers=response_headers,
    )


def internal_server_error(
    data: Dict[str, Any], response_headers: Dict[str, str] = None
) -> JSONResponse:
    return JSONResponse(
        content=data,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        headers=response_headers,
    )


def error_uploading_file(
    data: Dict[str, Any], response_headers: Dict[str, str] = None
) -> JSONResponse:
    return JSONResponse(
        content=data,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        headers=response_headers,
    )
