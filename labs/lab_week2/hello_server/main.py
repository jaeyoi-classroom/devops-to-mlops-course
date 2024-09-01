from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_docker():
    return "<p>Hello, Docker!</p>"