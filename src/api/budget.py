import sqlalchemy
from fastapi import APIRouter
from pydantic import BaseModel

from src import database as db
from src.sql_utils import get_category, get_user

router = APIRouter()

# TODO update all these endpoints considering they are now subsets of a the parent table "category"
@router.get("/users/{user_id}/budget/", tags=["budgets"])
def get_budget(user_id: int, budget_category_id: int = None):
    """
    This endpoint returns the user's budget information.
    By default, it will return all the user's budget information for all categories.

    - `budget_category_id`: the id of the category
    - `budget_category`: the user-defined name of a specific category
    - `budget`: the budget associated with the category
    - `expenses`: the expenses associated with each category
    - `budget_delta`: a number showing the difference between
      current money spent in the category and the budget in place

    Each expense is represented by a dictionary with the following keys:

    - `cost`: the monetary value of the expense, in dollars
    - `item`: the item associated with the expense
    - `date_time`: the date of the expense
    """
    data = []
    with db.engine.connect() as conn:
        user = get_user(user_id)
        if budget_category_id:
            category_user = get_category(user.user_id, budget_category_id)
            expenses = conn.execute(
                sqlalchemy.text('''
                SELECT * FROM expense
                WHERE category_id = :category_id
                '''),
                [{"user_id": user.user_id, "category_id": budget_category_id}]
            ).fetchall()
            expenses_list = []
            for expense in expenses:
                _, _, date_time, cost, description = expense
                expenses_list.append({
                    "date_time": date_time,
                    "cost": cost,
                    "item": description
                })
            data.append({
                "budget_category_id": budget_category_id,
                "budget_category": category_user.category_name,
                "budget": category_user.monthly_budget,
                "expenses": expenses_list,
                "budget_delta": category_user.monthly_budget - sum(
                    [expense["cost"] for expense in expenses_list]
                )
            })
        else:
            categories_user = conn.execute(
                sqlalchemy.text(
                    "SELECT * FROM budget_category WHERE user_id = :user_id"),
                [{"user_id": user[0]}]
            ).fetchall()
            for category_user in categories_user:
                expenses = conn.execute(
                    sqlalchemy.text('''
                    SELECT * FROM expense
                    WHERE category_id = :category_id
                    '''),
                    [{"user_id": user.user_id,
                      "category_id": category_user.category_id}]
                ).fetchall()
                expenses_list = []
                for expense in expenses:
                    _, _, date_time, cost, description = expense
                    expenses_list.append({
                        "date_time": date_time,
                        "cost": cost,
                        "item": description
                    })
                data.append({
                    "budget_category_id": category_user.category_id,
                    "budget_category": category_user.category_name,
                    "budget": category_user.monthly_budget,
                    "expenses": expenses_list,
                    "budget_delta": category_user.monthly_budget - sum(
                        [expense["cost"] for expense in expenses_list]
                    )
                })
    return data


class BudgetJson(BaseModel):
    budget: float


@router.post("/users/{user_id}/budget/{budget_category}/", tags=["budgets"])
def set_budget(user_id: int, budget_category: str, budget: BudgetJson):
    """
    This endpoint adds or updates a category with a budget. It takes as input:

    - `user_id`: the associated user for the budget
    - `budget_category`: the user generated category to be created/updated
    - `budget`: the dollar amount of the budget
    """
    with db.engine.connect() as conn:
        user = get_user(user_id)
        category_result = conn.execute(
            sqlalchemy.text('''
            SELECT * FROM budget_category
            WHERE user_id = :user_id
            AND category_name = :category_name
            '''),
            [{"user_id": user.user_id, "category_name": budget_category}]
        ).fetchone()
        if category_result is None:
            inserted_category = conn.execute(
                sqlalchemy.text('''
                INSERT INTO budget_category
                (category_name, user_id, monthly_budget)
                VALUES (:category_name, :user_id, :monthly_budget)
                RETURNING category_id
                '''),
                {"category_name": budget_category,
                 "user_id": user_id, "monthly_budget": budget.budget}
            )
            category_id = inserted_category.fetchone().category_id
            conn.commit()
            return {
                "category_id": category_id,
                "category_name": budget_category,
                "user_id": user.user_id,
                "monthly_budget": budget.budget
            }
        else:
            updated_category = conn.execute(
                sqlalchemy.text('''
                UPDATE budget_category
                SET monthly_budget = :monthly_budget
                WHERE category_id = :category_id
                RETURNING category_id
                '''),
                [{"monthly_budget": budget.budget,
                  "category_id": category_result.category_id}]
            )
            category_id = updated_category.fetchone().category_id
            conn.commit()
            return {
                "category_id": category_id,
                "category_name": budget_category,
                "user_id": user.user_id,
                "monthly_budget": budget.budget
            }
