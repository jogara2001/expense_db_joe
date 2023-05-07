import sqlalchemy
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src import database as db

router = APIRouter()

def check_user_exists(user_id: int):
    with db.engine.connect() as conn:
        user = conn.execute(
            sqlalchemy.text("SELECT * FROM user WHERE user_id = :user_id"),
            [{"user_id": user_id}]
        ).fetchone()
        if user is None:
            raise HTTPException(status_code=404, detail="user not found.")

def check_category_exists(user_id: int, budget_category_id: int):
    with db.engine.connect() as conn:
        category_user = conn.execute(
            sqlalchemy.text("SELECT * FROM budget_category WHERE user_id = :user_id AND category_id = :category_id"),
            [{"user_id": user_id, "category_id": budget_category_id}]
        ).fetchone()
        if category_user is None:
            raise HTTPException(status_code=404, detail="budget category not found.")

@router.get("/user/{user_id}/budget/", tags=["expenses"])
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
    data = []
    with db.engine.connect() as conn:
        check_user_exists(user_id)
        if budget_category_id:
            check_category_exists(user_id, budget_category_id)
            expenses = conn.execute(
                sqlalchemy.text("SELECT * FROM expense WHERE user_id = :user_id AND category_id = :category_id"),
                [{"user_id": user_id, "category_id": budget_category_id}]
            ).fetchall()
            expenses_list = []
            for expense in expenses:
                _, _, date, cost, _, description = expense
                expenses_list.append({
                    "date": date,
                    "cost": cost,
                    "item": description
                })
            data.append({
                "budget_category": category_user[1],
                "budget": category_user[3],
                "expenses": expenses_list,
                "budget_delta": category_user[3] - sum([expense["cost"] for expense in expenses_list])
            })
        else:
            categories_user = conn.execute(
                sqlalchemy.text("SELECT * FROM budget_category WHERE user_id = :user_id"),
                [{"user_id": user_id}]
            ).fetchall()
            for category_user in categories_user:
                expenses = conn.execute(
                    sqlalchemy.text("SELECT * FROM expense WHERE user_id = :user_id AND category_id = :category_id"),
                    [{"user_id": user_id, "category_id": category_user[0]}]
                ).fetchall()
                expenses_list = []
                for expense in expenses:
                    _, _, date, cost, _, description = expense
                    expenses_list.append({
                        "date": date,
                        "cost": cost,
                        "item": description
                    })
                data.append({
                    "budget_category": category_user[1],
                    "budget": category_user[3],
                    "expenses": expenses_list,
                    "budget_delta": category_user[3] - sum([expense["cost"] for expense in expenses_list])
                })
    return data


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
    with db.engine.connect() as conn:
        check_user_exists(user_id)
        category_result = conn.execute(
            sqlalchemy.text("SELECT * FROM budget_category WHERE user_id = :user_id AND category_name = :category_name"),
            [{"user_id": user_id, "category_name": budget_category}]
        ).fetchone()
        if category_result is None:
            current_max_row_id = conn.execute(
                sqlalchemy.text("SELECT MAX(category_id) FROM budget_category")
            ).fetchone()
            max_row_id = 0 if current_max_row_id is None else current_max_row_id[0] + 1
            conn.execute(
                sqlalchemy.text("INSERT INTO budget_category VALUES (:category_id, :category_name, :user_id, :monthly_budget)"),
                [{"category_id": max_row_id, "category_name": budget_category, "user_id": user_id, "monthly_budget": budget.budget}]
            )
            return {
                "category_id": max_row_id,
                "category_name": budget_category,
                "user_id": user_id,
                "monthly_budget": budget.budget
            }
        else:
            conn.execute(
                sqlalchemy.text("UPDATE budget_category SET monthly_budget = :monthly_budget WHERE category_id = :category_id"),
                [{"monthly_budget": budget.budget, "category_id": category_result[0]}]
            )
            return {
                "category_id": category_result[0],
                "category_name": category_result[1],
                "user_id": category_result[2],
                "monthly_budget": budget.budget
            }
