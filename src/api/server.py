from fastapi import FastAPI
from src.api import budget

description = ""

tags_metadata = [
]

app = FastAPI(
    title="Expense API",
    description=description,
    version="0.0.1",
    contact={
        "names": "Joe, Rahul, Ziadin",
        "email": "jogara@calpoly.edu ...",
    },
    openapi_tags=tags_metadata,
)
app.include_router(budget.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Expense API. See /docs for more information."}
