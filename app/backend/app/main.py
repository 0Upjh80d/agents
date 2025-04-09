import asyncio

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


def create_main_app():
    app = FastAPI()

    # Enable CORS
    origins = [
        "http://localhost:4200",
        "http://localhost:8000",
        "http://localhost:8001",
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
    app.include_router(clinic.router)
    app.include_router(record.router)
    app.include_router(user.router)
    app.include_router(vaccine.router)
    app.include_router(dummy_orchestrator.router)

    return app


def create_agent_app():
    app = FastAPI()
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
    app.include_router(chat.router)

    return app


app = create_main_app()
agent_app = create_agent_app()


@app.get("/")
async def root():
    return JSONResponse(content={"detail": "Hello World!"})


@agent_app.get("/")
async def agent_root():
    return JSONResponse(content={"detail": "Hello Agent!"})


async def run_apps():
    config_main = uvicorn.Config(
        "main:app", host="127.0.0.1", port=8000, reload=True, reload_dirs=["."]
    )
    config_agent = uvicorn.Config(
        "main:agent_app", host="127.0.0.1", port=8001, reload=True, reload_dirs=["."]
    )

    server_main = uvicorn.Server(config_main)
    server_agent = uvicorn.Server(config_agent)

    # Run both servers concurrently
    await asyncio.gather(server_main.serve(), server_agent.serve())


# main function to run the app
if __name__ == "__main__":
    asyncio.run(run_apps())
