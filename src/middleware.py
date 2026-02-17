from fastapi import FastAPI
from fastapi.requests import Request
import time
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

logger = logging.getLogger("uvicorn.access")
logger.disabled = True


def register_middleware(app: FastAPI):

    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        processing_time = time.time() - start_time

        message = f"{request.client.host} - {request.client.port} - {request.method} - {request.url.path} - completed after {processing_time}s"

        print(message)
        return response

    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_credentials=True
    )

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

    # We did this usinf dependency injection
    # @app.middleware('http')
    # async def auth(request: Request, call_next):
    #     if "Authorization" not in request.headers:
    #         return JSONResponse(
    #             content={
    #                 "message": "Not authenticated",
    #                 "resolution": "Please provide the right credentials"
    #             }
    #         )

    #     response = await call_next(request)

    #     return response
