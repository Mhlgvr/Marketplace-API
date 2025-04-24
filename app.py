from src.routes_init import init_routes
from flask import Flask

app = Flask(__name__)
init_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
