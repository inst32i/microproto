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
#    values,times, T = mf.calRisk(filename)
    return jsonify(Labels)

@app.route('/upload', methods=['POST', 'GET'])
def upload():
    print(request.files['pic_file'])
    if request.method == 'POST':
        f = request.files['pic_file']
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        upload_path = os.path.join(basepath, 'static/uploads',secure_filename(f.filename))  #注意：没有的文件夹一定要先创建，不然会提示没有该路径
        f.save(upload_path)
        resp = make_response(jsonify("static/uploads/"+f.filename))  # 响应体
        resp.headers["Access-Control-Allow-Origin"] = "*"  # 设置响应头
        return resp
    resp = make_response(jsonify("没有"))  # 响应体
    resp.headers["Access-Control-Allow-Origin"] = "*"  # 设置响应头
    return resp
if __name__ == '__main__':
    app.run(debug=True)
