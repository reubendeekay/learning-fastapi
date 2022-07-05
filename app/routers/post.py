from http import HTTPStatus
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from ..database import SessionLocal, get_db
from .. import models, schemas, oauth2


router = APIRouter(
    prefix="/posts",
    tags=["posts"],


)


@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: SessionLocal = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):

    return db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id).filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()


@router.get("/{post_id}", response_model=schemas.PostOut)
def get_post(post_id: int, db: SessionLocal = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    # cur.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
    # post = cur.fetchone()
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Post.id ==
                                                                                      models.Vote.post_id, isouter=True).group_by(models.Post.id).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/", status_code=HTTPStatus.CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: SessionLocal = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    # cur.execute("INSERT INTO posts (title, content) VALUES (%s, %s)",
    #             (new_post.title, new_post.content))
    # conn.commit()

    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.delete("/{post_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_post(post_id: int, db: SessionLocal = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    # cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id ==
                                              post_id)
    post = post_query.first()
    if post is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail="Post not found")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                            detail="You do not have permission to delete this post")
    post_query.delete(synchronize_session=False)
    db.commit()


@router.put("/{post_id}", status_code=HTTPStatus.OK)
def update_post(post_id: int, updated_post: schemas.PostCreate, db: SessionLocal = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    # cur.execute("UPDATE posts SET title = %s, content = %s WHERE id = %s",
    #             (updated_post.title, updated_post.content, post_id))
    # conn.commit()
    # if cur.rowcount == 0:
    post_query = db.query(models.Post).filter(
        models.Post.id == post_id)

    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail="Post not found")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                            detail="You do not have permission to delete this post")
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()

    return post.first()
