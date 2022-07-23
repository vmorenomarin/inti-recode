"""Lorem ipsum."""
from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def home():
    """Define a Teting function."""
    return{"message": "Init recode test."}
