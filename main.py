import uvicorn

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.const import static_dir, port
from app.handlers import router
from app.logger import LogConfig

def get_application() -> FastAPI:
    application = FastAPI()
    application.mount('/dashboard', StaticFiles(directory=static_dir), 'static')
    application.include_router(router)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return application


if __name__ == '__main__':
    app = get_application()
    uvicorn.run(app, host='0.0.0.0', port=port, log_config=LogConfig().model_dump())
