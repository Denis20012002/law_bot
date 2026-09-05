import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from presentation.api.answer import router as answer_router

from presentation.tgbot.main import bot, dp


def create_app():
    app: FastAPI = FastAPI()
    app.include_router(answer_router)
    app.mount("/static", StaticFiles(directory="static", html=True), name="static")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
