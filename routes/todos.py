# N/B this file was used to just display how to use flask-restful
# it is not part of the project

from flask import Flask
from flask_restful import Resource

app = Flask(__name__)

# todo crud
@app.get('/todos')
def get_todos():
    return []

@app.get("/todos/<int:id>")
def get_todo():
    return {}

@app.post("/todos")
def create_todo():
    return {"message": "created"}

@app.patch("/todos/<int:id>")
def update_todo():
    return {"message": "updated"}

@app.delete("/todos/<int:id>")
def delete_todo():
    return {"message": "deleted"}

class Todo(Resource):
    # create instance methods using http verbs as names
    def get(self, id = None):
        if id is None:
            return []
        else:
            return {}

    def post(self):
        return {"message": "created"}

    def patch(self, id):
        return {"message": "updated"}

    def delete(self, id):
        return {"message": "deleted"}

# O.O.P -> Object Oriented Programming -> blueprint of how objects are created
# inheritance, polymorphism, abstraction, encapsulation
# reusablity
