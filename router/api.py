from flask import Flask, request, jsonify
from flask_cors import CORS

from route import get_shortest_paths

app = Flask(__name__)
CORS(app)

@app.route('/route', methods = ['POST'])
def index():
    content = request.get_json()
    print(content)
    return get_shortest_paths(content)

if __name__ == '__main__':
    app.run(debug=True)