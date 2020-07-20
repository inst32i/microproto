# 小型安全度量系统原型

(基于flask - 后端工程)

## 配置说明

1.为了避免混乱,最好启用虚拟环境安装依赖,具体内容百度
	Windows激活虚拟环境:   source venv/Scripts/activate.bat
	Linux激活虚拟环境:     source venv/bin/activate
2.安装flask
	直接pip install flask 即可,缺什么装什么
3.安装Flask-CORS
	pip install Flask Flask-Cors
	这个拓展用于解决跨域问题
4.运行后端
	python app.py
	提示 Running on http://127.0.0.1:5000/ (默认端口5000)即启动成功

## 与前端进行数据交互

@app.route('/', methods=['GET'])
def ping_pong():
	return jsonify('Hello Flask')

对于以上内容,app.route用于构建api,
其中'/'表示当前端请求一个接口例如 'http://localhost:5000' 时,路由到这里
比如'/test'是后端接口,那么对应的请求就应该是'http://localhost:5000/test'
method一般为'GET'或者'POST',或者二者同时存在
return的一般是一个json格式的数据体,对应前端请求回调函数中的res