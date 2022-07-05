from .routers import user, post, auth, vote

from fastapi import Depends, FastAPI


from sqlalchemy.orm import Session
from . import models
from .database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)


app = FastAPI()


# Dependency injection


app.include_router(router=post.router)
app.include_router(router=user.router)
app.include_router(router=auth.router)
app.include_router(router=vote.router)


@app.get("/")
def root():
    return {"message": "Hello World"}
