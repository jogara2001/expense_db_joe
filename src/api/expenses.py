import datetime

import sqlalchemy
from fastapi import APIRouter
from pydantic import BaseModel

from src import database as db
from src import sql_utils as utils
from src.sql_utils import get_category

router = APIRouter()


@router.get("/user/{user_id}/expense/{expense_id}", tags=["expenses"])
def get_expense(user_id: int, expense_id: int):
    """
    This endpoint returns the information associated with an expense by its identifier.
    For each expense it returns:

    - `cost`: the monetary value of the expense, in Dollars
    - `date_time`: the date and time of the expense
    - `expense_id`: the ID of the item associated with the expense
    - `category`: the user defined category of the item
    - `description`: the user defined description of the item
    """
    user = utils.get_user(user_id)
    expense_id, category_id, date_time, cost, description = utils.get_expense(
        expense_id)
    category = utils.get_category(user.user_id, category_id)
    return {
        "cost": cost,
        "date_time": date_time,
        "expense_id": expense_id,
        "category": category.category_name,
        "description": description,
    }


@router.get("/user/{user_id}/expenses", tags=["expenses"])
def list_expenses(user_id: int,
                  start_date: str = (
                          datetime.datetime.utcnow() - datetime.timedelta(days=7)
                  ).strftime("%Y-%m-%d %H:%M:%S"),
                  end_date: str = datetime.datetime
                  .utcnow().strftime("%Y-%m-%d %H:%M:%S")):
    """
    This endpoint returns the information associated with expenses
    over a defined time period.
    By default, the difference between `start_date` and `end_date` is one week
    and `end_time` is today.
    Expects format "YYYY-MM-DD HH:MM:SS" for timestamp

    For each expense, it returns:

    - `cost`: the monetary value of the expense, in dollars
    - `date`: the date of the expense
    - `expense_id`: the ID of the item associated with the expense
    - `category`: the user-defined category of the item
    """

    with db.engine.connect() as conn:
        expenses = conn.execute(sqlalchemy.text(
            '''
            SELECT expense_id, budget_category.category_id, 
            date_time, cost, description, category_name
            FROM expense
            JOIN budget_category on budget_category.category_id = expense.category_id
            JOIN "user" on "user".user_id = budget_category.user_id
            WHERE "user".user_id = :user_id_input
            AND date_time <= :end_date AND date_time >= :start_date;
            ''',
        ),
            {
                "user_id_input": user_id,
                "end_date": end_date,
                "start_date": start_date,
            }
        ).fetchall()
        return [
            {
                "expense_id": expense.expense_id,
                "cost": expense.cost,
                "date_time": expense.date_time,
                "description": expense.description,
                "category": expense.category_name,
            }
            for expense in expenses
        ]


# Expects format "YYYY-MM-DD HH:MM:SS" for timestamp
class ExpenseJson(BaseModel):
    cost: float
    date_time: str
    category_id: int
    description: str


@router.post("/user/{user_id}/expense/", tags=["expenses"])
def add_expense(user_id: int, expense_json: ExpenseJson):
    """
    This endpoint adds a new expense to the database.
    This expense includes:

    - `user`: the user who is adding the expense (required)
    - `cost`: the monetary value of the expense, in Dollars (required)
    - `date_time`: the date and time of the expense. (required)
            Expects format "YYYY-MM-DD HH:MM:SS"
    - `category_id`: the budget category of the item (required)
    - `description`: the user defined description of the item (not required)
    """

    # check user has category specified
    get_category(user_id, expense_json.category_id)

    with db.engine.connect() as conn:
        inserted_expense = conn.execute(
            sqlalchemy.text(
                '''
                INSERT INTO expense (category_id, date_time, cost, description)
                VALUES (:category_id, :date_time, :cost, :description)
                RETURNING expense_id;
            '''
            ),
            {
                "category_id": expense_json.category_id,
                "date_time": expense_json.date_time,
                "cost": expense_json.cost,
                "description": expense_json.description
            }
        )
        expense = inserted_expense.fetchone()
        conn.commit()
    return {
        "expense_id": expense.expense_id,
        "category_id": expense_json.category_id,
        "date_time": expense_json.date_time,
        "cost": expense_json.cost,
        "description": expense_json.description,
    }
