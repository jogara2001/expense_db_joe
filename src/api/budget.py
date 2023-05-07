import sqlalchemy
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src import database as db

router = APIRouter()


@router.get("/user/{user_id}/budget/{budget_category_id}", tags=["expenses"])
def get_budget(user_id: int, budget_category_id: int):
    """
    This endpoint returns the user's budget information.
    By default, it will return all the user's budget information for all categories.

    - `budget_category`: the user-defined name of a specific category
    - `budget`: the budget associated with the category
    - `expenses`: the expenses associated with each category
    - `budget_delta`: a number showing the difference between current money spent in the category and the budget in place

    Each expense is represented by a dictionary with the following keys:

    - `cost`: the monetary value of the expense, in dollars
    - `item`: the item associated with the expense
    - `date`: the date of the expense
    """
    json = None

    with db.engine.connect() as conn:
        result = conn.execute("").fetchone()
        if result is None:
            raise HTTPException(status_code=404, detail="expense not found.")

    return json


class BudgetJson(BaseModel):
    budget: float


@router.post("/user/{user_id}/budget/{budget_category}/", tags=["movies"])
def set_budget(user_id: int, budget_category: str, budget: BudgetJson):
    """
    This endpoint adds or updates a category with a budget. It takes as input:

    - `user_id`: the associated user for the budget
    - `budget_category`: the user generated category to be created/updated
    - `budget`: the dollar amount of the budget
    """
    json = None

    with db.engine.connect() as conn:
        result = conn.execute("")
        if result is None:
            raise HTTPException(status_code=404, detail="")

    return json
