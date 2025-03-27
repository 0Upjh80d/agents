import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from routers import authentication, booking, chat, clinic, record, user, vaccine


def create_app():
    app = FastAPI()
    app.include_router(authentication.router)
    app.include_router(booking.router)
    app.include_router(chat.router)
    app.include_router(clinic.router)
    app.include_router(record.router)
    app.include_router(user.router)
    app.include_router(vaccine.router)
    return app


app = create_app()


@app.get("/")
async def root():
    return JSONResponse(content={"detail": "Hello World!"})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
