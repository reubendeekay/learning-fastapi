from http import HTTPStatus
from this import d
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from .. import oauth2, database, schemas, models


router = APIRouter(
    prefix="/vote",
    tags=["vote"]
)


@router.post("/", status_code=HTTPStatus.CREATED)
def vote(user_vote: schemas.Vote, db: database.SessionLocal = Depends(database.get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(
        models.Post.id == user_vote.post_id).first()
    if post is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail="Post not found")

    # sourcery skip: merge-else-if-into-elif
    vote_query = db.query(models.Vote).filter(
        models.Vote.user_id == current_user.id, models.Vote.post_id == user_vote.post_id)
    vote_found = vote_query.first()
    if (user_vote.dir == 1):
        if vote_found is not None:
            raise HTTPException(status_code=HTTPStatus.CONFLICT,
                                detail="You already voted for this post")

        new_vote = models.Vote(
            user_id=current_user.id,
            post_id=user_vote.post_id
        )
        db.add(new_vote)
        db.refresh(new_vote)
    else:
        if vote_found:

            vote_query.delete(synchronize_session=False)
        else:
            raise HTTPException(status_code=HTTPStatus.CONFLICT,
                                detail="You have not voted for this post")

    db.commit()


@router.get("/",)
def get_votes(db: database.SessionLocal = Depends(database.get_db)):
    return db.query(models.Vote).all()


@router.delete('/', status_code=HTTPStatus.NO_CONTENT)
def delete_votes(db: database.SessionLocal = Depends(database.get_db)):
    votes_query = db.query(models.Vote)
    if(votes_query.first() is not None):
        votes_query.delete(synchronize_session=False)
        db.commit()
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail="No votes to delete")
