from flask import Flask, jsonify, request
from flask_cors import CORS
import manifoldAlgorithm as mf
app = Flask(__name__)
CORS(app)
@app.route('/', methods=['GET','POST'])
def ping_pong():
    filename = 'testData.csv'
#    return jsonify(request.args.get('ID'))
    Labels = mf.getLabel(filename)
    values,times, T = mf.calRisk(filename)
    return jsonify(Labels)
if __name__ == '__main__':
    app.run(debug=True)