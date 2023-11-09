import argparse

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from api.controllers import data_preparation_controller,health_controller
import uvicorn
from containers import Application

application = Application()

app = FastAPI(version='1.0.0', title='CV_UsefullFunctions',
              description="API for training StableDiffusion models using Stable diffusion v1.5")

application.wire(modules=[data_preparation_controller, inference_controller, training_controller, models_controller, job_controller])

app.application = application

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    health_controller.router,
    prefix="/health",
    tags=["Health Check"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    models_controller.router,
    tags=["Models"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    data_preparation_controller.router,
    tags=["Data_Preparation"],
    responses={404: {"description": "Not found"}},
)
app.include_router(
    training_controller.router,
    tags=["Training"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    inference_controller.router,
    tags=["Inference"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    job_controller.router,
    tags=["Job"],
    responses={404: {"description": "Not found"}},
)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help="Host IP to run on", type=str, default="0.0.0.0")
    parser.add_argument('--port', help="Port to run on", type=int, default=7861)
    parser.add_argument('--log-config', help="Logging configuration file", type=str, default="assets/log_conf.ini")
    parser.add_argument('--workers', help="Number of workers", type=int, default=1)
    parser.add_argument('--reload', help="Reload API on change", action='store_true')
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port, workers=args.workers, reload=args.reload, log_config=args.log_config)
