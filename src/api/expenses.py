import sqlalchemy
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src import database as db
from src import sql_utils as utils

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
    user = utils.get_user(user_id)
    expense_id, _, date, cost, category_id, description = utils.get_expense(
        expense_id)
    category = utils.get_category(user[0], category_id)
    return {
        "cost": cost,
        "date": date,
        "expense_id": expense_id,
        "category": category[1],
        "description": description,
    }


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
    with db.engine.connect() as conn:
        expenses = conn.execute(sqlalchemy.text('''
            SELECT expense_id, category_id, date, cost, description
            FROM expense;
            ''')).fetchall()
        return [
            {
                "expense_id": expense[0],
                "cost": expense[1],
                "date": expense[2],
                "description": expense[3],
                "category": expense[4],
                "budget_delta": expense[5],
            }
            for expense in expenses
        ]


class ExpenseJson(BaseModel):
    cost: float
    date: int
    category: str
    description: str


@router.post("/user/{user_id}/expense/", tags=["expenses"])
def add_expense(user_id: int, expense: ExpenseJson):
    """
    This endpoint adds a new expense to the database.
    This expense includes some required data and some optional data:

    - `user`: the user who is adding the expense (required)
    - `cost`: the monetary value of the expense, in Dollars (required)
    - `date`: the date of the expense (required)
    - `category`: the user defined category of the item (not required)
    - `description`: the user defined description of the item (not required)
    """
    with db.engine.connect() as conn:
        inserted_expense = conn.execute(sqlalchemy.text('''
            INSERT INTO expense (category_id, cost, description)
            VALUES (:category_id, :cost, :description)
            RETURNING expense_id;
            '''),
                                        {"category_id": expense.category,
                                         "cost": expense.cost,
                                         "description": expense.description}
                                        )
        expense_id = inserted_expense.fetchone()[0]
        conn.commit()
    return {
        "expense_id": expense_id,
        "category_id": expense.category,
        "cost": expense.cost,
        "description": expense.description,
    }
