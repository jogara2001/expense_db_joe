import sqlalchemy
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src import database as db

router = APIRouter()


@router.get("/user/{user_id}/expense/{expense_id}", tags=["expenses"])
def get_expense(user_id: int, expense_id: int):
    """
    This endpoint returns the information associated with an expense by its identifier.
    For each expense it returns:

    - `cost`: the monetary value of the expense, in Dollars
    - `date`: the date of the expense
    - `expense_id`: the ID of the item associated with the expense
    - `category`: the user defined category of the item
    - `description`: the user defined description of the item
    """
    json = None

    with db.engine.connect() as conn:
        result = conn.execute("").fetchone()
        if result is None:
            raise HTTPException(status_code=404, detail="expense not found.")

    return json


@router.get("/user/{user_id}/expenses", tags=["expenses"])
def list_expenses(user_id: int):
    """
    This endpoint returns the information associated with expenses over a defined time period.
    By default, the difference between `start_time` and `end_time` is one week and `end_time` is today.
    For each expense, it returns:

    - `cost`: the monetary value of the expense, in dollars
    - `date`: the date of the expense
    - `expense_id`: the ID of the item associated with the expense
    - `category`: the user-defined category of the item
    - `budget_delta`: a number showing the difference between current money spent in the category and the budget in place
    """
    json = None

    with db.engine.connect() as conn:
        result = conn.execute("")

    return json


class ExpenseJson(BaseModel):
    cost: float
    date: int
    category: str
    description: str


@router.post("/user/{user_id}/expense/", tags=["movies"])
def add_conversation(user_id: int, expense: ExpenseJson):
    """
    This endpoint adds a new expense to the database.
    This expense includes some required data and some optional data:

    - `user`: the user who is adding the expense (required)
    - `cost`: the monetary value of the expense, in Dollars (required)
    - `date`: the date of the expense (required)
    - `category`: the user defined category of the item (not required)
    - `description`: the user defined description of the item (not required)
    """
    json = None

    with db.engine.connect() as conn:
        result = conn.execute("")
        if result is None:
            raise HTTPException(status_code=404, detail="")

    return json
