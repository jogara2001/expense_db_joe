import sqlalchemy
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src import database as db

router = APIRouter()


@router.get("/user/", tags=["users"])
def list_users():
    """
    This endpoint returns the information associated with all users.
    For each user it returns:

    - `user_id`: the ID of the user
    - `name`: the name of the user
    """
    with db.engine.connect() as conn:
      users = conn.execute(
        sqlalchemy.text('SELECT * FROM "user"')
      ).fetchall()
    return [
      {
        "user_id": user[0],
        "name": user[1],
      }
      for user in users
    ]

@router.get("/user/{user_id}/", tags=["users"])
def get_user(user_id: int):
    """
    This endpoint returns the information associated with a user by its identifier.
    For each user it returns:

    - `user_id`: the ID of the user
    - `name`: the name of the user
    """
    with db.engine.connect() as conn:
      user = conn.execute(
        sqlalchemy.text('SELECT * FROM "user" WHERE user_id = :user_id'),
        [{"user_id": user_id}]
      ).fetchone()
      if user is None:
        raise HTTPException(status_code=404, detail="user not found.")
    return {
      "user_id": user[0],
      "name": user[1],
    }

class UserJson(BaseModel):
    name: str

@router.post("/user/", tags=["users"])
def create_user(user: UserJson):
    """
    This endpoint creates a new user.

    Takes in a UserJson which contains the user's name.

    Returns the user's ID and name if successful.
    """
    with db.engine.connect() as conn:
      inserted_user = conn.execute(
        sqlalchemy.text('INSERT INTO "user" (name) VALUES (:name) RETURNING user_id'),
        [{"name": user.name}]
      )
      user_id = inserted_user.fetchone()[0]
      conn.commit()
    return {
      "user_id": user_id,
      "user_name": user.name,
    }
