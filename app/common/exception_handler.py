from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.common.exceptions import AppException

# Exception template
# {
#     "message": "invalid request",
#     "detail": [],
# }


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message, "detail": jsonable_encoder(exc.detail)},
    )


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    try:
        message = errors[0]["ctx"]["reason"]
    except KeyError:
        message = errors[0]["msg"]
    return JSONResponse(
        status_code=422,
        content={"message": message, "detail": jsonable_encoder(errors)},
    )
