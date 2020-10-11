# -*- coding:utf-8 -*-
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import manifoldAlgorithm as mf
import os
import json
from werkzeug.utils import secure_filename

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
    if request.method == 'POST':
        f = request.files['pic_file']
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        upload_path = os.path.join(basepath, 'uploads',secure_filename(f.filename))  #注意：没有的文件夹一定要先创建，不然会提示没有该路径
        f.save(upload_path)
        # Labels = mf.getLabel("uploads/"+f.filename)
        rootPath = os.path.split(os.path.realpath(__file__))[0]
        Labels, selectLabels = mf.getLabel(rootPath + "/uploads/" + f.filename)
        # Labels = [1, 2, 3]
        print(selectLabels)
        result = {
            "labels":Labels,
            "selectLabels":selectLabels,
            "path": rootPath + "/uploads/" + f.filename
        }
        resp = make_response(jsonify(result))  # 响应体
        resp.headers["Access-Control-Allow-Origin"] = "*"  # 设置响应头
        return resp
    resp = make_response(jsonify("没有"))  # 响应体
    resp.headers["Access-Control-Allow-Origin"] = "*"  # 设置响应头
    return resp

@app.route('/calc', methods=['POST', 'GET'])
def calrisk():
    if request.method == 'POST':
        data = json.loads(request.get_data("data"))
        labels = data["checkedLabels"]
        path = data["filePath"]
        ipIdxList, ipLocByIdx, pairs = pairsOfIp(path)
        values, times, T = mf.calRisk(path, labels)
        result = {                           #result保存时间与风险倍数
                "ipIdxList":ipIdxList
                "ipLocByIdx":ipLocByIdx
                "pairs":pairs
                "time":T,
                "value": times	
        }
        resp = make_response(jsonify(result))  # 响应体
        resp.headers["Access-Control-Allow-Origin"] = "*"  # 设置响应头
        return resp
    resp = make_response(jsonify("没有"))  # 响应体
    resp.headers["Access-Control-Allow-Origin"] = "*"  # 设置响应头
    return resp
if __name__ == '__main__':
    app.run(debug=True)
