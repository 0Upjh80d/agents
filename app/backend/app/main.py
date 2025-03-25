import uvicorn
from fastapi import FastAPI
from routers import authentication, booking, chat, record, stock, user


def create_app():
    app = FastAPI()
    app.include_router(chat.router)
    app.include_router(user.router)
    app.include_router(booking.router)
    app.include_router(stock.router)
    app.include_router(record.router)
    app.include_router(authentication.router)
    return app


app = create_app()


@app.get("/")
def root():
    return {"message": "Hello World", "detail": "Successfully deployed CI/CD pipeline"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
