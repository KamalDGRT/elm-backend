from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def delete_response(response_content: dict = {"message": "Deleted successfully!"}):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(response_content)
    )
