# https://fastapi.tiangolo.com/tutorial/first-steps/
# How to run the code: uvicorn app.main:app --reload

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers.auth import role
from app.routers.auth import user
from app.routers.auth import login
from app.routers.auth import signup
from app.routers.root import user as root_user


app = FastAPI(
    title="RBAC API",
    description="API for all of RBAC Stuff!",
    version="0.1.0",
    contact={"name": "Kamal Sharma", "url": "https://github.com/KamalDGRT"},
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

# use the imported router in your project here:
# app.include_router(module1.router)
app.include_router(role.router)
app.include_router(user.router)
app.include_router(login.router)
app.include_router(signup.router)
app.include_router(root_user.router)


@app.get("/")
async def root_endpoint():
    deployment = {"dev": "Development", "qa": "QA", "uat": "UAT", "prod": "RBAC"}
    depl_env = deployment.get(settings.deployment_env, "")

    return {"message": f"{ depl_env } API is running successfully!"}
