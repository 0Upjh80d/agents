import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from routers import (
    authentication,
    booking,
    chat,
    clinic,
    dummy_orchestrator,
    record,
    user,
    vaccine,
)
from starlette.middleware.cors import CORSMiddleware


def create_app():
    app = FastAPI()

    # Enable CORS
    origins = [
        "http://localhost:4200",
        "http://localhost:8000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(authentication.router)
    app.include_router(booking.router)
    app.include_router(chat.router)
    app.include_router(clinic.router)
    app.include_router(record.router)
    app.include_router(user.router)
    app.include_router(vaccine.router)
    app.include_router(dummy_orchestrator.router)
    return app


app = create_app()


@app.get("/")
async def root():
    return JSONResponse(content={"detail": "Hello World!"})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
