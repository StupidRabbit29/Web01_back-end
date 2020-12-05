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



if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)


