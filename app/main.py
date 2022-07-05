from .routers import user, post, auth, vote

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine


models.Base.metadata.create_all(bind=engine)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)


# Dependency injection


app.include_router(router=post.router)
app.include_router(router=user.router)
app.include_router(router=auth.router)
app.include_router(router=vote.router)


@app.get("/")
def root():
    return {"message": "Hello World"}
