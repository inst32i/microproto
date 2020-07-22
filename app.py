from flask import Flask, jsonify, request
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
@app.route('/', methods=['GET','POST'])
def ping_pong():
    return jsonify(request.args.get('ID'))
if __name__ == '__main__':
    app.run(debug=True)