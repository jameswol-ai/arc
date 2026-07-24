# api/index.py
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Flask is running on Vercel!"

@app.route("/test")
def test():
    return "Test route works"