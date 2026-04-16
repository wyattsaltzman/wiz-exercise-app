import os
import sys
from bson import ObjectId
from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    print("ERROR: MONGO_URI environment variable is not set", file=sys.stderr)
    sys.exit(1)

client = MongoClient(MONGO_URI)
db = client["tododb"]
todos_col = db["todos"]

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def index(request: Request):
    todos = list(todos_col.find().sort("created_at", -1))
    return templates.TemplateResponse("index.html", {"request": request, "todos": todos})


@app.post("/todo")
def add_todo(task: str = Form("")):
    if task.strip():
        todos_col.insert_one({"task": task.strip(), "done": False})
    return RedirectResponse(url="/", status_code=303)


@app.post("/todo/{todo_id}/toggle")
def toggle_todo(todo_id: str):
    todo = todos_col.find_one({"_id": ObjectId(todo_id)})
    if todo:
        todos_col.update_one(
            {"_id": ObjectId(todo_id)},
            {"$set": {"done": not todo["done"]}},
        )
    return RedirectResponse(url="/", status_code=303)


@app.post("/todo/{todo_id}/delete")
def delete_todo(todo_id: str):
    todos_col.delete_one({"_id": ObjectId(todo_id)})
    return RedirectResponse(url="/", status_code=303)
