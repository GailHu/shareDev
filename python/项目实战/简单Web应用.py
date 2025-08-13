# 项目实战：简单Web应用
# 使用Flask框架

from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to my first Flask app!"

if __name__ == "__main__":
    app.run(debug=True)