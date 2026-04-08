from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.common import ErrorResponse


def _response(status_code: int, code: str, message: str, details: object | None = None) -> JSONResponse:
    payload = ErrorResponse(code=code, message=message, details=details).model_dump()
    return JSONResponse(status_code=status_code, content=payload)


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        if isinstance(exc.detail, dict):
            code = str(exc.detail.get("code", "http_error"))
            message = str(exc.detail.get("message", "HTTP error"))
            details = exc.detail.get("details")
        else:
            code = "http_error"
            message = str(exc.detail)
            details = None
        return _response(exc.status_code, code, message, details)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return _response(422, "validation_error", "Request validation failed", exc.errors())

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        return _response(500, "internal_error", "Unexpected server error", str(exc))
