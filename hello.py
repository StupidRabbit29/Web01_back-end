from flask import Flask
from markupsafe import escape
import flask_cors
import flask_restful as restful

app = Flask(__name__)
# 允许跨域请求，因为后端是运行在5000端口上的，而前端是3000端口
flask_cors.CORS(app, supports_credentials=True)


@app.route('/login/<username>')
def show_user_profile(username):
    # show the user profile for that user
    print('User %s' % escape(username))
    return {
        'result': 'success'
    }


# 在 Terminal 中，运行以下命令来运行该应用（ PyCharm 中自带的 Terminal 是可以的）
# set FLASK_APP=hello.py
# flask run
# 然后在浏览器中访问 http://127.0.0.1:5000/ 即可
# 注意这只是一个简单的内建服务器，只能用于测试，不能用于生产

# flask 的输出信息
# Environment: production
# WARNING: This is a development server. Do not use it in a production deployment.
# Use a production WSGI server instead.
# Debug mode: off

# 打开网页之后，如果想要修改代码，还要重启，如果开启了 Debug 模式，服务器能自动重载，同时还能提供一个 debugger
# 输入命令
# set FLASK_ENV=development
# 这完成了以下三件事
    # 1. it activates the debugger
    # 2. it activates the automatic reloader
    # 3. it enables the debug mode on the Flask application.
# 也可以使用 set FLASK_DEBUG=1





